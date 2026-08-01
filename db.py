"""
Shared SQLite database layer.
bot.py এবং webapp.py দুটোই এই মডিউল থেকে ডাটা রিড/রাইট করে।
"""

import sqlite3
from datetime import datetime

from config import DB_PATH


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
    c.execute("""
        CREATE TABLE IF NOT EXISTS ad_rewards (
            ymid TEXT PRIMARY KEY,
            user_id INTEGER,
            points INTEGER,
            credited_at TEXT
        )
    """)
    defaults = {"referral_enabled": "1", "promo_enabled": "1", "ads_enabled": "1", "force_join_enabled": "1"}
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


def record_ad_reward(ymid: str, user_id: int, points: int) -> bool:
    """Monetag postback থেকে আসা ad reward ক্রেডিট করে। একই ymid দুইবার ক্রেডিট হবে না (ডুপ্লিকেট প্রোটেকশন)।
    সফল হলে True, আগে থেকেই ক্রেডিট করা থাকলে False রিটার্ন করে।"""
    conn = get_conn()
    existing = conn.execute("SELECT 1 FROM ad_rewards WHERE ymid=?", (ymid,)).fetchone()
    if existing:
        conn.close()
        return False
    conn.execute(
        "INSERT INTO ad_rewards (ymid, user_id, points, credited_at) VALUES (?, ?, ?, ?)",
        (ymid, user_id, points, datetime.utcnow().isoformat()),
    )
    conn.execute("UPDATE users SET points = points + ? WHERE user_id=?", (points, user_id))
    conn.commit()
    conn.close()
    return True


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
