"""
Bot configuration.

লোকালি টেস্ট করার সময় নিচে সরাসরি বসাতে পারেন।
কিন্তু GitHub এ আপলোড করার আগে এখান থেকে টোকেন/আইডি সরিয়ে ফেলুন —
Render এ Environment Variables হিসেবে বসাবেন (README.md দেখুন)।
"""

import os

# 1) @BotFather থেকে পাওয়া টোকেন
BOT_TOKEN = os.environ.get("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")

# 2) আপনার Telegram User ID (একাধিক হলে কমা দিয়ে দিন, যেমন: "123,456")
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "123456789").split(",") if x.strip()]

# 3) আপনার বটের ইউজারনেম (@ ছাড়া)
BOT_USERNAME = os.environ.get("BOT_USERNAME", "your_bot_username")

# 4) ডাটাবেজ ফাইলের নাম
DB_PATH = os.environ.get("DB_PATH", "bot.db")

# 5) রেফারেল রিওয়ার্ড পয়েন্ট
REFERRAL_REWARD = int(os.environ.get("REFERRAL_REWARD", "20"))

# 6) Mini App এর পাবলিক URL (Render এ ডিপ্লয় করার পর পাবেন, যেমন https://your-app.onrender.com)
MINI_APP_URL = os.environ.get("MINI_APP_URL", "https://your-app.onrender.com")

# ---------------------------------------------------------------------------
# 7) ফোর্স-জয়েন চ্যানেল/গ্রুপ — বট ব্যবহার করার আগে ইউজারকে এগুলোতে জয়েন করতে হবে
# ---------------------------------------------------------------------------
#
# চ্যানেল ১: পাবলিক চ্যানেল (ইউজারনেম দিয়ে ভেরিফাই করা যায়)
CHANNEL_1_TITLE = os.environ.get("CHANNEL_1_TITLE", "BDincomeTV")
CHANNEL_1_LINK = os.environ.get("CHANNEL_1_LINK", "https://t.me/BDincomeTV")
CHANNEL_1_USERNAME = os.environ.get("CHANNEL_1_USERNAME", "BDincomeTV")  # @ ছাড়া

# চ্যানেল/গ্রুপ ২: প্রাইভেট গ্রুপ (ইনভাইট লিংক দিয়ে জয়েন হয়, ইউজারনেম নেই)
# এটা ভেরিফাই করতে হলে বটকে এই গ্রুপে Admin বানাতে হবে, এবং গ্রুপের numeric Chat ID লাগবে।
# Chat ID বের করার উপায়: বটকে গ্রুপে অ্যাড করে অ্যাডমিন বানান, তারপর গ্রুপে যেকোনো মেসেজ
# @RawDataBot বা @getidsbot কে ফরওয়ার্ড করুন — ওখান থেকে "chat":{"id": -100xxxxxxxxxx} পাবেন।
# CHANNEL_2_ID খালি রাখলে এই গ্রুপের জয়েন-চেক স্কিপ হয়ে যাবে (লিংক তবুও দেখানো হবে না)।
CHANNEL_2_TITLE = os.environ.get("CHANNEL_2_TITLE", "আমাদের চ্যাট গ্রুপ")
CHANNEL_2_LINK = os.environ.get("CHANNEL_2_LINK", "https://t.me/+ghnv_A6HgAM3Yzll-")
CHANNEL_2_ID = os.environ.get("CHANNEL_2_ID", "")  # যেমন: -1001234567890

# ---------------------------------------------------------------------------
# 8) Monetag বিজ্ঞাপন (Rewarded Ad) সেটিংস
# ---------------------------------------------------------------------------
# Monetag ড্যাশবোর্ড (monetag.com) থেকে Rewarded Interstitial zone বানিয়ে zone ID বসান
MONETAG_ZONE_ID = os.environ.get("MONETAG_ZONE_ID", "")  # খালি রাখলে Ad বাটন Mini App এ দেখাবে না

# Monetag ড্যাশবোর্ডের "Get SDK" থেকে পাওয়া স্ক্রিপ্ট URL (এটা অ্যাকাউন্ট-ভিত্তিক আলাদা হতে পারে,
# ড্যাশবোর্ড থেকে হুবহু কপি করে এখানে বসান — নিচের ভ্যালুটা শুধু ডিফল্ট প্লেসহোল্ডার)
MONETAG_SDK_SRC = os.environ.get("MONETAG_SDK_SRC", "https://libtl.com/sdk.js")

# একটা বিজ্ঞাপন দেখলে (Monetag যদি "valued" কনফার্ম করে) ইউজার কত পয়েন্ট পাবে
AD_REWARD_POINTS = int(os.environ.get("AD_REWARD_POINTS", "5"))

# Postback URL সুরক্ষিত রাখতে একটা গোপন কোড — Monetag Postback URL এ এই secret বসাবেন
# (নিচে README এ উদাহরণ আছে)। নিজে একটা র‍্যান্ডম স্ট্রিং বসিয়ে নিন।
MONETAG_POSTBACK_SECRET = os.environ.get("MONETAG_POSTBACK_SECRET", "change-this-secret")

# ---------------------------------------------------------------------------
# 9) Withdraw (টাকা তোলার) সিস্টেম
# ---------------------------------------------------------------------------
# কোন কোন পেমেন্ট মেথড দেখাবে (কমা দিয়ে আলাদা)
WITHDRAW_METHODS = [m.strip() for m in os.environ.get("WITHDRAW_METHODS", "bKash,Nagad,Rocket").split(",") if m.strip()]

# পয়েন্ট থেকে টাকায় কনভার্সন রেট — যেমন 10 মানে "১০ পয়েন্ট = ১ টাকা"
POINTS_TO_TAKA_RATE = int(os.environ.get("POINTS_TO_TAKA_RATE", "10"))

# একবারে সর্বনিম্ন কত পয়েন্ট withdraw করা যাবে
MIN_WITHDRAW_POINTS = int(os.environ.get("MIN_WITHDRAW_POINTS", "100"))
