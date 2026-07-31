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
