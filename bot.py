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
import random
import string

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import (
    BOT_TOKEN,
    ADMIN_IDS,
    BOT_USERNAME,
    REFERRAL_REWARD,
    MINI_APP_URL,
    CHANNEL_1_TITLE,
    CHANNEL_1_LINK,
    CHANNEL_1_USERNAME,
    CHANNEL_2_TITLE,
    CHANNEL_2_LINK,
    CHANNEL_2_ID,
)
from keep_alive import keep_alive
from db import (
    init_db,
    get_setting,
    set_setting,
    get_or_create_user,
    add_points,
    get_user,
    bump_referral_count,
    all_user_ids,
    user_stats,
    create_promo,
    redeem_promo,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


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
# ফোর্স-জয়েন (Mandatory Channel/Group Join) সিস্টেম
# ---------------------------------------------------------------------------

REQUIRED_CHANNELS = []
if CHANNEL_1_USERNAME:
    REQUIRED_CHANNELS.append(
        {"title": CHANNEL_1_TITLE, "link": CHANNEL_1_LINK, "chat_ref": f"@{CHANNEL_1_USERNAME}"}
    )
if CHANNEL_2_ID:
    REQUIRED_CHANNELS.append(
        {"title": CHANNEL_2_TITLE, "link": CHANNEL_2_LINK, "chat_ref": CHANNEL_2_ID}
    )
elif CHANNEL_2_LINK:
    # Chat ID সেট করা নেই, তাই ভেরিফাই করা যাবে না — শুধু info হিসেবে রাখা হলো, ব্লক করবে না
    logger.warning(
        "CHANNEL_2_ID সেট করা নেই, তাই '%s' গ্রুপের জয়েন-চেক স্কিপ হয়ে যাবে।", CHANNEL_2_TITLE
    )


async def get_unjoined_channels(bot, user_id: int):
    """যেসব চ্যানেল/গ্রুপে ইউজার এখনো জয়েন করেননি, সেগুলোর লিস্ট রিটার্ন করে।"""
    if not get_setting("force_join_enabled"):
        return []
    missing = []
    for ch in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch["chat_ref"], user_id=user_id)
            if member.status in ("left", "kicked"):
                missing.append(ch)
        except Exception as e:
            # বট যদি ঐ চ্যানেলে অ্যাডমিন না হয়, বা চ্যাট খুঁজে না পায় — তাহলে ইউজারকে আটকানো হবে না
            logger.warning("'%s' চ্যানেলের মেম্বারশিপ চেক করা যায়নি: %s", ch["title"], e)
    return missing


def join_prompt_markup(missing) -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(f"📢 {ch['title']} জয়েন করুন", url=ch["link"])] for ch in missing]
    keyboard.append([InlineKeyboardButton("✅ জয়েন করেছি — ভেরিফাই করুন", callback_data="verify_join")])
    return InlineKeyboardMarkup(keyboard)


async def send_join_prompt(update: Update, missing):
    text = (
        "🔒 <b>বট ব্যবহার করার আগে</b> নিচের চ্যানেল/গ্রুপে জয়েন করা বাধ্যতামূলক:\n\n"
        + "\n".join(f"• {ch['title']}" for ch in missing)
        + "\n\nজয়েন করার পর নিচের ✅ বাটনে চাপুন।"
    )
    if update.callback_query:
        await update.callback_query.message.reply_text(
            text, parse_mode=ParseMode.HTML, reply_markup=join_prompt_markup(missing)
        )
    else:
        await update.message.reply_text(
            text, parse_mode=ParseMode.HTML, reply_markup=join_prompt_markup(missing)
        )


async def ensure_joined(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """True রিটার্ন করে যদি ইউজার সব প্রয়োজনীয় চ্যানেলে জয়েন থাকে, নাহলে প্রম্পট পাঠিয়ে False দেয়।"""
    user = update.effective_user
    missing = await get_unjoined_channels(context.bot, user.id)
    if missing:
        await send_join_prompt(update, missing)
        return False
    return True


def welcome_text(user) -> str:
    text = (
        f"স্বাগতম, {user.first_name}! 👋\n\n"
        "এই বট দিয়ে আপনি পারবেন:\n"
        "🔗 /myref — আপনার রেফারেল লিংক পান, বন্ধুদের ইনভাইট করে পয়েন্ট জিতুন\n"
        "🎁 /redeem <code> — প্রোমো কোড রিডিম করুন\n"
        "💰 /balance — আপনার পয়েন্ট ব্যালেন্স দেখুন\n"
        "🚀 /app — সুন্দর Mini App খুলুন\n"
        "❓ /help — সাহায্য"
    )
    text += ads_footer()
    return text


def persistent_app_keyboard() -> ReplyKeyboardMarkup:
    """চ্যাটের নিচে সবসময় স্থায়ীভাবে থাকা 'Open App' বাটন — একবার পাঠালে এটা লেগেই থাকবে।"""
    return ReplyKeyboardMarkup(
        [[KeyboardButton("🚀 Open App", web_app=WebAppInfo(url=MINI_APP_URL))]],
        resize_keyboard=True,
        is_persistent=True,
    )


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

    if not await ensure_joined(update, context):
        return

    await update.message.reply_text(
        welcome_text(user), parse_mode=ParseMode.HTML, reply_markup=persistent_app_keyboard()
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 <b>কমান্ড লিস্ট</b>\n\n"
        "/start — বট শুরু করুন\n"
        "/myref — আপনার রেফারেল লিংক ও পরিসংখ্যান\n"
        "/redeem &lt;code&gt; — প্রোমো কোড রিডিম করুন\n"
        "/balance — পয়েন্ট ব্যালেন্স দেখুন\n"
        "/app — Mini App খুলুন\n"
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


async def app_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username or user.first_name)
    if not await ensure_joined(update, context):
        return
    await update.message.reply_text(
        "🚀 নিচের বাটনে চাপুন Mini App খুলতে (বাটনটা সবসময় নিচে থাকবে):",
        reply_markup=persistent_app_keyboard(),
    )


async def myref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username or user.first_name)
    if not await ensure_joined(update, context):
        return
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
    if not await ensure_joined(update, context):
        return
    u = get_user(user.id)
    await update.message.reply_text(f"💰 আপনার ব্যালেন্স: <b>{u['points']}</b> পয়েন্ট", parse_mode=ParseMode.HTML)


async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username or user.first_name)
    if not await ensure_joined(update, context):
        return

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
    force_join = "🟢 Force-Join: ON" if get_setting("force_join_enabled") else "🔴 Force-Join: OFF"

    keyboard = [
        [InlineKeyboardButton(ref, callback_data="toggle_referral_enabled")],
        [InlineKeyboardButton(promo, callback_data="toggle_promo_enabled")],
        [InlineKeyboardButton(ads, callback_data="toggle_ads_enabled")],
        [InlineKeyboardButton(force_join, callback_data="toggle_force_join_enabled")],
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


async def verify_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    missing = await get_unjoined_channels(context.bot, user.id)

    if missing:
        await query.answer("❌ এখনো সব চ্যানেলে জয়েন করেননি। আগে জয়েন করুন।", show_alert=True)
        return

    await query.answer("✅ ভেরিফাই সফল!")
    try:
        await query.message.delete()
    except Exception:
        pass
    await context.bot.send_message(
        chat_id=user.id,
        text=welcome_text(user),
        parse_mode=ParseMode.HTML,
        reply_markup=persistent_app_keyboard(),
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
    app.add_handler(CommandHandler("app", app_cmd))
    app.add_handler(CommandHandler("myref", myref))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("redeem", redeem))

    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("addpromo", addpromo))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("stats", stats_cmd))

    app.add_handler(CallbackQueryHandler(verify_join_callback, pattern="^verify_join$"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(toggle_|show_stats)"))

    logger.info("Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
