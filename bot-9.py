"""
Professional Telegram Bot — Referral + Promo Code + Ads/Broadcast System
=========================================================================

Features:
- /start with referral tracking (unique referral link per user, points on referral)
- Promo code redemption system (admin creates codes with reward + usage limit)
- Ads/Broadcast system (admin can send a message to all users)
- Full Admin Panel with inline buttons to turn ON/OFF:
    - Referral system
    - Promo code system
    - Ads/footer banner shown to users
- User commands: /start, /balance, /myref, /redeem <code>, /help
- Admin commands: /admin, /addpromo, /broadcast, /stats

Requirements: python-telegram-bot>=21.0  (pip install -r requirements.txt)
Run: python bot.py
"""

import logging
import sqlite3
import random
import string
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN, ADMIN_IDS, DB_PATH, BOT_USERNAME, REFERRAL_REWARD
from keep_alive import keep_alive

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DATABASE LAYER
# ---------------------------------------------------------------------------

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            points INTEGER DEFAULT 0,
            referred_by INTEGER,
            referral_count INTEGER DEFAULT 0,
            joined_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes (
            code TEXT PRIMARY KEY,
            reward INTEGER,
            max_uses INTEGER,
            used_count INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS promo_redemptions (
            user_id INTEGER,
            code TEXT,
            redeemed_at TEXT,
            PRIMARY KEY (user_id, code)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    # default settings (feature toggles)
    defaults = {"referral_enabled": "1", "promo_enabled": "1", "ads_enabled": "1"}
    for k, v in defaults.items():
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
    conn.commit()
    conn.close()


def get_setting(key: str) -> bool:
    conn = get_conn()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return bool(row and row["value"] == "1")


def set_setting(key: str, value: bool):
    conn = get_conn()
    conn.execute("UPDATE settings SET value=? WHERE key=?", ("1" if value else "0", key))
    conn.commit()
    conn.close()


def get_or_create_user(user_id: int, username: str, referred_by: int = None) -> bool:
    """Returns True if this is a newly created user."""
    conn = get_conn()
    row = conn.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,)).fetchone()
    if row:
        conn.close()
        return False
    conn.execute(
        "INSERT INTO users (user_id, username, points, referred_by, joined_at) VALUES (?, ?, 0, ?, ?)",
        (user_id, username, referred_by, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    return True


def add_points(user_id: int, amount: int):
    conn = get_conn()
    conn.execute("UPDATE users SET points = points + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()


def get_user(user_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return row


def bump_referral_count(referrer_id: int):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET referral_count = referral_count + 1 WHERE user_id=?", (referrer_id,)
    )
    conn.commit()
    conn.close()


def all_user_ids():
    conn = get_conn()
    rows = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()
    return [r["user_id"] for r in rows]


def user_stats():
    conn = get_conn()
    total_users = conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
    total_points = conn.execute("SELECT SUM(points) s FROM users").fetchone()["s"] or 0
    total_referrals = conn.execute("SELECT SUM(referral_count) s FROM users").fetchone()["s"] or 0
    conn.close()
    return total_users, total_points, total_referrals


def create_promo(code: str, reward: int, max_uses: int):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO promo_codes (code, reward, max_uses, used_count, active, created_at) "
        "VALUES (?, ?, ?, COALESCE((SELECT used_count FROM promo_codes WHERE code=?), 0), 1, ?)",
        (code, reward, max_uses, code, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_promo(code: str):
    conn = get_conn()
    row = conn.execute("SELECT * FROM promo_codes WHERE code=?", (code,)).fetchone()
    conn.close()
    return row


def redeem_promo(user_id: int, code: str) -> str:
    """Returns a status string: 'ok', 'invalid', 'inactive', 'exhausted', 'already_used'."""
    conn = get_conn()
    promo = conn.execute("SELECT * FROM promo_codes WHERE code=?", (code,)).fetchone()
    if not promo:
        conn.close()
        return "invalid"
    if not promo["active"]:
        conn.close()
        return "inactive"
    if promo["used_count"] >= promo["max_uses"]:
        conn.close()
        return "exhausted"
    already = conn.execute(
        "SELECT 1 FROM promo_redemptions WHERE user_id=? AND code=?", (user_id, code)
    ).fetchone()
    if already:
        conn.close()
        return "already_used"

    conn.execute("UPDATE promo_codes SET used_count = used_count + 1 WHERE code=?", (code,))
    conn.execute(
        "INSERT INTO promo_redemptions (user_id, code, redeemed_at) VALUES (?, ?, ?)",
        (user_id, code, datetime.utcnow().isoformat()),
    )
    conn.execute("UPDATE users SET points = points + ? WHERE user_id=?", (promo["reward"], user_id))
    conn.commit()
    conn.close()
    return "ok"


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def ads_footer() -> str:
    if get_setting("ads_enabled"):
        return "\n\n📢 <i>Sponsored: Check out our latest offers with /help</i>"
    return ""


def gen_random_code(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


# ---------------------------------------------------------------------------
# USER COMMANDS
# ---------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    referred_by = None

    if context.args:
        arg = context.args[0]
        if arg.startswith("ref_"):
            try:
                candidate = int(arg.replace("ref_", ""))
                if candidate != user.id:
                    referred_by = candidate
            except ValueError:
                pass

    is_new = get_or_create_user(user.id, user.username or user.first_name, referred_by)

    if is_new and referred_by and get_setting("referral_enabled"):
        referrer = get_user(referred_by)
        if referrer:
            add_points(referred_by, REFERRAL_REWARD)
            bump_referral_count(referred_by)
            try:
                await context.bot.send_message(
                    chat_id=referred_by,
                    text=f"🎉 আপনার রেফারেল লিংক দিয়ে নতুন একজন যোগ দিয়েছে! আপনি পেয়েছেন +{REFERRAL_REWARD} পয়েন্ট।",
                )
            except Exception:
                pass

    text = (
        f"স্বাগতম, {user.first_name}! 👋\n\n"
        "এই বট দিয়ে আপনি পারবেন:\n"
        "🔗 /myref — আপনার রেফারেল লিংক পান, বন্ধুদের ইনভাইট করে পয়েন্ট জিতুন\n"
        "🎁 /redeem <code> — প্রোমো কোড রিডিম করুন\n"
        "💰 /balance — আপনার পয়েন্ট ব্যালেন্স দেখুন\n"
        "❓ /help — সাহায্য"
    )
    text += ads_footer()
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 <b>কমান্ড লিস্ট</b>\n\n"
        "/start — বট শুরু করুন\n"
        "/myref — আপনার রেফারেল লিংক ও পরিসংখ্যান\n"
        "/redeem &lt;code&gt; — প্রোমো কোড রিডিম করুন\n"
        "/balance — পয়েন্ট ব্যালেন্স দেখুন\n"
    )
    if is_admin(update.effective_user.id):
        text += (
            "\n<b>👑 অ্যাডমিন কমান্ড</b>\n"
            "/admin — অ্যাডমিন প্যানেল খুলুন\n"
            "/addpromo &lt;code&gt; &lt;reward&gt; &lt;max_uses&gt; — নতুন প্রোমো কোড\n"
            "/broadcast &lt;message&gt; — সব ইউজারকে মেসেজ পাঠান\n"
            "/stats — বট পরিসংখ্যান দেখুন\n"
        )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def myref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username or user.first_name)
    u = get_user(user.id)
    link = f"https://t.me/{BOT_USERNAME}?start=ref_{user.id}"

    status = "✅ চালু আছে" if get_setting("referral_enabled") else "⛔ বন্ধ আছে (অ্যাডমিন কর্তৃক)"
    text = (
        f"🔗 <b>আপনার রেফারেল লিংক:</b>\n{link}\n\n"
        f"👥 মোট রেফার করেছেন: <b>{u['referral_count']}</b> জন\n"
        f"💰 বর্তমান পয়েন্ট: <b>{u['points']}</b>\n"
        f"⚙️ রেফারেল সিস্টেম: {status}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username or user.first_name)
    u = get_user(user.id)
    await update.message.reply_text(f"💰 আপনার ব্যালেন্স: <b>{u['points']}</b> পয়েন্ট", parse_mode=ParseMode.HTML)


async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username or user.first_name)

    if not get_setting("promo_enabled"):
        await update.message.reply_text("⛔ প্রোমো কোড সিস্টেম বর্তমানে বন্ধ আছে।")
        return

    if not context.args:
        await update.message.reply_text("ব্যবহার: /redeem CODE123")
        return

    code = context.args[0].upper().strip()
    result = redeem_promo(user.id, code)

    messages = {
        "ok": "✅ প্রোমো কোড সফলভাবে রিডিম হয়েছে! পয়েন্ট যোগ হয়েছে আপনার ব্যালেন্সে।",
        "invalid": "❌ এই কোডটি সঠিক নয়।",
        "inactive": "⛔ এই কোডটি বর্তমানে নিষ্ক্রিয়।",
        "exhausted": "⚠️ এই কোডের ব্যবহারসীমা শেষ হয়ে গেছে।",
        "already_used": "⚠️ আপনি ইতিমধ্যে এই কোডটি ব্যবহার করেছেন।",
    }
    await update.message.reply_text(messages[result])


# ---------------------------------------------------------------------------
# ADMIN COMMANDS
# ---------------------------------------------------------------------------

def admin_panel_markup() -> InlineKeyboardMarkup:
    ref = "🟢 Referral: ON" if get_setting("referral_enabled") else "🔴 Referral: OFF"
    promo = "🟢 Promo: ON" if get_setting("promo_enabled") else "🔴 Promo: OFF"
    ads = "🟢 Ads: ON" if get_setting("ads_enabled") else "🔴 Ads: OFF"

    keyboard = [
        [InlineKeyboardButton(ref, callback_data="toggle_referral_enabled")],
        [InlineKeyboardButton(promo, callback_data="toggle_promo_enabled")],
        [InlineKeyboardButton(ads, callback_data="toggle_ads_enabled")],
        [InlineKeyboardButton("📊 Stats দেখুন", callback_data="show_stats")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ এই কমান্ড শুধুমাত্র অ্যাডমিনদের জন্য।")
        return
    await update.message.reply_text(
        "👑 <b>অ্যাডমিন প্যানেল</b>\nনিচের বাটনগুলো ট্যাপ করে ফিচার অন/অফ করুন:",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_panel_markup(),
    )


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⛔ আপনি অ্যাডমিন নন।", show_alert=True)
        return

    if query.data.startswith("toggle_"):
        key = query.data.replace("toggle_", "")
        current = get_setting(key)
        set_setting(key, not current)
        await query.answer(f"{key} এখন {'ON' if not current else 'OFF'}")
        await query.edit_message_reply_markup(reply_markup=admin_panel_markup())

    elif query.data == "show_stats":
        total_users, total_points, total_referrals = user_stats()
        await query.answer()
        await query.message.reply_text(
            f"📊 <b>বট পরিসংখ্যান</b>\n\n"
            f"👥 মোট ইউজার: {total_users}\n"
            f"💰 মোট বিতরণকৃত পয়েন্ট: {total_points}\n"
            f"🔗 মোট রেফারেল: {total_referrals}",
            parse_mode=ParseMode.HTML,
        )


async def addpromo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ এই কমান্ড শুধুমাত্র অ্যাডমিনদের জন্য।")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "ব্যবহার: /addpromo <code> <reward> [max_uses]\n"
            "উদাহরণ: /addpromo WELCOME50 50 100\n"
            "কোড না দিলে র‍্যান্ডম কোড জেনারেট হবে: /addpromo auto 50 100"
        )
        return

    code = args[0].upper().strip()
    if code == "AUTO":
        code = gen_random_code()

    try:
        reward = int(args[1])
        max_uses = int(args[2]) if len(args) > 2 else 1
    except ValueError:
        await update.message.reply_text("reward এবং max_uses অবশ্যই সংখ্যা হতে হবে।")
        return

    create_promo(code, reward, max_uses)
    await update.message.reply_text(
        f"✅ প্রোমো কোড তৈরি হয়েছে!\n\nকোড: <code>{code}</code>\nরিওয়ার্ড: {reward} পয়েন্ট\nসর্বোচ্চ ব্যবহার: {max_uses} জন",
        parse_mode=ParseMode.HTML,
    )


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ এই কমান্ড শুধুমাত্র অ্যাডমিনদের জন্য।")
        return

    if not context.args:
        await update.message.reply_text("ব্যবহার: /broadcast আপনার মেসেজ এখানে লিখুন")
        return

    message = " ".join(context.args)
    users = all_user_ids()
    sent, failed = 0, 0

    status_msg = await update.message.reply_text(f"📤 ব্রডকাস্ট শুরু হচ্ছে... ({len(users)} ইউজার)")

    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 <b>ঘোষণা</b>\n\n{message}", parse_mode=ParseMode.HTML)
            sent += 1
        except Exception:
            failed += 1

    await status_msg.edit_text(f"✅ ব্রডকাস্ট সম্পন্ন!\n\nপাঠানো হয়েছে: {sent}\nব্যর্থ: {failed}")


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ এই কমান্ড শুধুমাত্র অ্যাডমিনদের জন্য।")
        return
    total_users, total_points, total_referrals = user_stats()
    await update.message.reply_text(
        f"📊 <b>বট পরিসংখ্যান</b>\n\n"
        f"👥 মোট ইউজার: {total_users}\n"
        f"💰 মোট বিতরণকৃত পয়েন্ট: {total_points}\n"
        f"🔗 মোট রেফারেল: {total_referrals}",
        parse_mode=ParseMode.HTML,
    )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    init_db()
    keep_alive()  # Render free tier কে জাগিয়ে রাখার জন্য ওয়েব সার্ভার চালু
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("myref", myref))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("redeem", redeem))

    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("addpromo", addpromo))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("stats", stats_cmd))

    app.add_handler(CallbackQueryHandler(admin_callback))

    logger.info("Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
