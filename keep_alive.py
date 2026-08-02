"""
Render.com এর Free Web Service ১৫ মিনিট নিষ্ক্রিয় থাকলে ঘুমিয়ে যায় — তাই এই ফাইলটা
একটা ওয়েব সার্ভার চালু রাখে (UptimeRobot এটাকে পিং করবে)।

একই সার্ভার Telegram Mini App-ও সার্ভ করে:
- স্ট্যাটিক ফাইল (static/index.html) — Mini App এর UI
- /api/me      — ইউজারের ব্যালেন্স, রেফারেল লিংক, ও ফোর্স-জয়েন স্ট্যাটাস রিটার্ন করে
- /api/redeem  — প্রোমো কোড রিডিম করে
"""

import hashlib
import hmac
import json
import os
import threading
from urllib.parse import parse_qsl

import requests
from flask import Flask, jsonify, request, send_from_directory

from config import (
    BOT_TOKEN,
    BOT_USERNAME,
    CHANNEL_1_TITLE,
    CHANNEL_1_LINK,
    CHANNEL_1_USERNAME,
    CHANNEL_2_TITLE,
    CHANNEL_2_LINK,
    CHANNEL_2_ID,
    MONETAG_ZONE_ID,
    MONETAG_SDK_SRC,
    AD_REWARD_POINTS,
    MONETAG_POSTBACK_SECRET,
)
from db import (
    init_db,
    get_setting,
    get_or_create_user,
    get_user,
    redeem_promo,
    record_ad_reward,
)

app = Flask(__name__, static_folder="static", static_url_path="")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

REQUIRED_CHANNELS = []
if CHANNEL_1_USERNAME:
    REQUIRED_CHANNELS.append(
        {"title": CHANNEL_1_TITLE, "link": CHANNEL_1_LINK, "chat_ref": f"@{CHANNEL_1_USERNAME}"}
    )
if CHANNEL_2_ID:
    REQUIRED_CHANNELS.append(
        {"title": CHANNEL_2_TITLE, "link": CHANNEL_2_LINK, "chat_ref": CHANNEL_2_ID}
    )


# ---------------------------------------------------------------------------
# Telegram Mini App initData ভেরিফিকেশন (নিরাপত্তার জন্য বাধ্যতামূলক)
# https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
# ---------------------------------------------------------------------------

def validate_init_data(init_data: str):
    """initData সঠিক ও Telegram থেকে এসেছে কিনা যাচাই করে।
    সফল হলে (user_dict, None) রিটার্ন করে, ব্যর্থ হলে (None, reason_code) রিটার্ন করে —
    reason_code দিয়ে বোঝা যায় ঠিক কোথায় সমস্যা হলো (ডিবাগ করার জন্য দরকারি)।"""
    if not init_data:
        return None, "empty_init_data"
    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
        received_hash = parsed.pop("hash", None)
        if not received_hash:
            return None, "no_hash_field"

        # Telegram এর অফিসিয়াল নিয়ম: শুধু 'hash' ফিল্ড বাদ দিয়ে বাকি সব ফিল্ড দিয়ে
        # data-check-string বানাতে হয় (signature সহ, যদি থাকে)
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(computed_hash, received_hash):
            print(f"[monetag-auth-debug] hash mismatch. keys received: {list(parsed.keys())}")
            return None, "hash_mismatch"

        user_json = parsed.get("user")
        if not user_json:
            return None, "no_user_field"
        return json.loads(user_json), None
    except Exception as e:
        print(f"[monetag-auth-debug] exception while validating initData: {e}")
        return None, "exception"


def get_unjoined_channels(user_id: int):
    if not get_setting("force_join_enabled"):
        return []
    missing = []
    for ch in REQUIRED_CHANNELS:
        try:
            resp = requests.get(
                f"{TELEGRAM_API}/getChatMember",
                params={"chat_id": ch["chat_ref"], "user_id": user_id},
                timeout=10,
            ).json()
            if not resp.get("ok"):
                # বট হয়তো এই চ্যানেলে Admin না, বা চ্যাট খুঁজে পায়নি —
                # এক্ষেত্রে ইউজারকে আটকানো হবে না, শুধু লগে জানিয়ে রাখা হচ্ছে
                print(f"[force-join] '{ch['title']}' চেক করা যায়নি: {resp.get('description')}")
                continue
            status = resp.get("result", {}).get("status")
            if status in ("left", "kicked"):
                missing.append({"title": ch["title"], "link": ch["link"]})
        except Exception as e:
            print(f"[force-join] '{ch['title']}' চেক করার সময় এরর: {e}")
            continue
    return missing


# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/health")
def health():
    return "✅ Telegram bot is alive and running!"


@app.route("/api/me", methods=["POST"])
def api_me():
    body = request.get_json(silent=True) or {}
    tg_user, reason = validate_init_data(body.get("initData", ""))
    if not tg_user:
        print(f"[api/me] validation failed, reason={reason}")
        return jsonify({"ok": False, "error": "invalid_init_data", "reason": reason}), 401

    user_id = tg_user["id"]
    get_or_create_user(user_id, tg_user.get("username") or tg_user.get("first_name", "user"))

    missing = get_unjoined_channels(user_id)
    if missing:
        return jsonify({"ok": False, "need_join": True, "channels": missing})

    u = get_user(user_id)
    referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
    return jsonify(
        {
            "ok": True,
            "need_join": False,
            "first_name": tg_user.get("first_name", ""),
            "points": u["points"],
            "referral_count": u["referral_count"],
            "referral_link": referral_link,
            "promo_enabled": get_setting("promo_enabled"),
            "monetag_zone_id": MONETAG_ZONE_ID,
            "monetag_sdk_src": MONETAG_SDK_SRC,
            "ad_reward_points": AD_REWARD_POINTS,
        }
    )


@app.route("/api/redeem", methods=["POST"])
def api_redeem():
    body = request.get_json(silent=True) or {}
    tg_user, reason = validate_init_data(body.get("initData", ""))
    if not tg_user:
        print(f"[api/redeem] validation failed, reason={reason}")
        return jsonify({"ok": False, "error": "invalid_init_data", "reason": reason}), 401

    user_id = tg_user["id"]
    missing = get_unjoined_channels(user_id)
    if missing:
        return jsonify({"ok": False, "need_join": True, "channels": missing})

    if not get_setting("promo_enabled"):
        return jsonify({"ok": False, "status": "disabled"})

    code = (body.get("code") or "").strip().upper()
    if not code:
        return jsonify({"ok": False, "status": "invalid"})

    get_or_create_user(user_id, tg_user.get("username") or tg_user.get("first_name", "user"))
    result = redeem_promo(user_id, code)
    u = get_user(user_id)
    return jsonify({"ok": True, "status": result, "points": u["points"]})


@app.route("/api/monetag/postback")
def monetag_postback():
    """
    Monetag তাদের সার্ভার থেকে সরাসরি এই URL হিট করে (ইউজারের ব্রাউজার থেকে না) —
    এটাই সবচেয়ে নিরাপদ পদ্ধতি, কারণ ফ্রন্টএন্ড থেকে জাল কল করে পয়েন্ট নেওয়া যাবে না।
    Monetag ড্যাশবোর্ডে Postback URL হিসেবে বসাতে হবে (README এ উদাহরণ আছে):

    https://your-app.onrender.com/api/monetag/postback?secret=YOUR_SECRET&ymid={ymid}&event={event_type}&value={reward_event_type}&telegram_id={telegram_id}
    """
    if request.args.get("secret") != MONETAG_POSTBACK_SECRET:
        return "forbidden", 403

    ymid = request.args.get("ymid")
    telegram_id = request.args.get("telegram_id")
    reward_event_type = request.args.get("value")  # 'valued' or 'non_valued'

    if not ymid or not telegram_id:
        return "missing ymid/telegram_id", 400

    if reward_event_type != "valued":
        # বিজ্ঞাপনটা মনিটাইজড হয়নি (fraud/ফিল্টার হওয়া ট্রাফিক) — পয়েন্ট দেওয়া হবে না
        return "ok (not valued, skipped)", 200

    try:
        user_id = int(telegram_id)
    except ValueError:
        return "bad telegram_id", 400

    get_or_create_user(user_id, "ad_viewer")
    credited = record_ad_reward(ymid, user_id, AD_REWARD_POINTS)
    return ("ok (credited)" if credited else "ok (duplicate, skipped)"), 200


def run():
    init_db()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()
