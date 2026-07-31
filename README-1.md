# 🤖 Telegram Referral + Promo + Ads Bot — সেটআপ গাইড

## ✨ ফিচারসমূহ
- **রেফারেল সিস্টেম** — প্রতিটা ইউজারের নিজস্ব রেফারেল লিংক, নতুন কেউ জয়েন করলে পয়েন্ট
- **প্রোমো কোড সিস্টেম** — অ্যাডমিন কোড বানাবে, ইউজার `/redeem` দিয়ে রিডিম করবে
- **Ads/Broadcast সিস্টেম** — সব ইউজারকে একসাথে মেসেজ পাঠানো যাবে
- **Admin Panel** — বাটন ক্লিক করে Referral / Promo / Ads অন-অফ করা যাবে, স্ট্যাটস দেখা যাবে

---

## 🚀 ধাপে ধাপে সেটআপ

### ধাপ ১: বট তৈরি করুন
1. টেলিগ্রামে **@BotFather** কে মেসেজ দিন
2. `/newbot` কমান্ড দিন, নাম ও ইউজারনেম দিন
3. যে টোকেন পাবেন সেটা কপি করে রাখুন (যেমন: `123456:ABC-DEF...`)

### ধাপ ২: নিজের User ID বের করুন
1. **@userinfobot** কে টেলিগ্রামে মেসেজ দিন
2. সে আপনার Numeric ID দেখাবে (যেমন: `987654321`) — এটাই আপনার Admin ID

### ধাপ ৩: config.py ফাইল এডিট করুন
`config.py` ফাইল খুলে নিচের ৩টা জিনিস বসান:
```python
BOT_TOKEN = "আপনার আসল টোকেন এখানে"
ADMIN_IDS = [987654321]   # আপনার ID
BOT_USERNAME = "your_bot_username"   # @ ছাড়া বটের ইউজারনেম
```

### ধাপ ৪: ইনস্টল করুন
```bash
pip install -r requirements.txt
```

### ধাপ ৫: বট চালু করুন
```bash
python bot.py
```
টার্মিনালে "Bot starting..." দেখলে বুঝবেন বট চলছে। এখন টেলিগ্রামে গিয়ে বটকে `/start` দিন।

> ⚠️ বটটা ২৪/৭ চালু রাখতে চাইলে **VPS** (Ubuntu server), **Railway.app**, বা **Render.com**-এ হোস্ট করতে হবে — নিজের কম্পিউটার বন্ধ করলে বট বন্ধ হয়ে যাবে।

---

## 👑 অ্যাডমিন কমান্ডসমূহ

| কমান্ড | কাজ |
|---|---|
| `/admin` | অন/অফ প্যানেল খোলে (বাটন দিয়ে Referral/Promo/Ads টগল করুন) |
| `/addpromo CODE 50 100` | নতুন প্রোমো কোড — কোড=CODE, রিওয়ার্ড=৫০ পয়েন্ট, সর্বোচ্চ ১০০ জন ব্যবহার করতে পারবে |
| `/addpromo auto 50 100` | র‍্যান্ডম কোড অটো-জেনারেট করবে |
| `/broadcast আপনার মেসেজ` | সব ইউজারকে একসাথে মেসেজ পাঠাবে (Ads/ঘোষণার জন্য) |
| `/stats` | মোট ইউজার, পয়েন্ট, রেফারেল সংখ্যা দেখাবে |

## 👤 ইউজার কমান্ডসমূহ
| কমান্ড | কাজ |
|---|---|
| `/start` | বট শুরু, রেফারেল লিংক দিয়ে এলে পয়েন্ট যোগ হয় |
| `/myref` | নিজের রেফারেল লিংক ও পরিসংখ্যান |
| `/balance` | পয়েন্ট ব্যালেন্স |
| `/redeem CODE` | প্রোমো কোড রিডিম |
| `/help` | সব কমান্ডের তালিকা |

---

## 🔧 কাস্টমাইজেশন
- **রেফারেল রিওয়ার্ড বদলাতে**: `config.py`-তে `REFERRAL_REWARD` বদলান
- **স্বাগতম মেসেজ বদলাতে**: `bot.py`-এর `start()` ফাংশনে টেক্সট এডিট করুন
- **Ads footer এর টেক্সট বদলাতে**: `bot.py`-এর `ads_footer()` ফাংশন দেখুন

## 📂 ফাইল স্ট্রাকচার
```
telegram_bot/
├── bot.py            ← মূল বট কোড
├── config.py         ← টোকেন, অ্যাডমিন আইডি ইত্যাদি
├── requirements.txt  ← প্রয়োজনীয় লাইব্রেরি
├── bot.db            ← ডাটাবেজ (প্রথমবার রান করলে অটো তৈরি হবে)
└── README.md         ← এই গাইড
```

---

## 🌐 GitHub + Render + UptimeRobot দিয়ে ২৪/৭ চালু রাখা (ফ্রি)

এই সেটআপ করলে আপনার কম্পিউটার বন্ধ থাকলেও বট সবসময় চালু থাকবে।

### ধাপ ১: GitHub এ কোড আপলোড করুন
1. **github.com** এ গিয়ে অ্যাকাউন্ট খুলুন (না থাকলে)
2. উপরে ডানপাশে **"+"** → **New repository**
3. Repository name দিন (যেমন: `telegram-bot`), **Private** সিলেক্ট করুন (নিরাপত্তার জন্য Public না করাই ভালো), **Create repository** চাপুন
4. এই ফোল্ডারের সব ফাইল (`bot.py`, `config.py`, `keep_alive.py`, `requirements.txt`, `Procfile`, `.gitignore`) আপনার কম্পিউটারে রাখুন, তারপর repository পেজে **"uploading an existing file"** লিংকে ক্লিক করে সব ফাইল ড্র্যাগ করে দিন
5. নিচে **Commit changes** বাটনে ক্লিক করুন

> ⚠️ **গুরুত্বপূর্ণ**: `config.py`-তে আসল `BOT_TOKEN` বা `ADMIN_IDS` বসাবেন না, কারণ কোডটা এখন `os.environ.get()` দিয়ে Environment Variable থেকে ভ্যালু নেয়। `config.py`-তে ডিফল্ট প্লেসহোল্ডার রেখেই আপলোড করুন। আসল টোকেন বসবে Render এর Environment Variables সেকশনে (নিচে ধাপ ৩ দেখুন)।

### ধাপ ২: Render এ অ্যাকাউন্ট খুলুন ও সার্ভিস তৈরি করুন
1. **render.com** এ গিয়ে **Sign Up** করুন (GitHub দিয়ে সাইন আপ করলে সহজ হবে)
2. Dashboard থেকে **New +** → **Web Service** সিলেক্ট করুন
3. আপনার GitHub রিপোজিটরি (`telegram-bot`) কানেক্ট করুন এবং সিলেক্ট করুন
4. সেটিংস দিন:
   - **Name**: যেকোনো নাম (যেমন: `my-telegram-bot`)
   - **Region**: যেকোনো একটা কাছাকাছি (Singapore হলে ভালো)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Instance Type**: **Free** সিলেক্ট করুন

### ধাপ ৩: Environment Variables বসান (টোকেন এখানে দিন)
"Environment Variables" সেকশনে গিয়ে **Add Environment Variable** দিয়ে একে একে যোগ করুন:

| Key | Value |
|---|---|
| `BOT_TOKEN` | আপনার BotFather থেকে পাওয়া আসল টোকেন |
| `ADMIN_IDS` | আপনার Telegram User ID (যেমন: `987654321`) |
| `BOT_USERNAME` | আপনার বটের ইউজারনেম (@ ছাড়া) |
| `REFERRAL_REWARD` | `20` (চাইলে বদলান) |

সব বসানো হলে নিচে **Create Web Service** বাটনে ক্লিক করুন। Render বিল্ড শুরু করবে — ২-৫ মিনিট লাগতে পারে। লগে "Bot starting..." দেখলে বুঝবেন বট চালু হয়ে গেছে।

Render আপনাকে একটা URL দেবে, যেমন:
```
https://my-telegram-bot.onrender.com
```
এই URL কপি করে রাখুন, পরের ধাপে লাগবে।

### ধাপ ৪: UptimeRobot দিয়ে সবসময় জাগিয়ে রাখুন
Render এর ফ্রি প্ল্যান ১৫ মিনিট কেউ ভিজিট না করলে ঘুমিয়ে যায়। এটা ঠেকাতে:

1. **uptimerobot.com** এ গিয়ে ফ্রি অ্যাকাউন্ট খুলুন
2. Dashboard থেকে **+ Add New Monitor** ক্লিক করুন
3. সেটিংস দিন:
   - **Monitor Type**: `HTTP(s)`
   - **Friendly Name**: `Telegram Bot Keep Alive`
   - **URL**: আপনার Render URL (ধাপ ৩ থেকে পাওয়া, যেমন `https://my-telegram-bot.onrender.com`)
   - **Monitoring Interval**: `5 minutes`
4. **Create Monitor** ক্লিক করুন

ব্যাস! এখন UptimeRobot প্রতি ৫ মিনিটে আপনার বটের সার্ভারকে পিং করবে, ফলে Render কখনো ঘুমাবে না এবং বট ২৪/৭ চালু থাকবে।

### ✅ চেক করুন সব ঠিক আছে কিনা
- Render এর **Logs** ট্যাবে গিয়ে দেখুন "Bot starting..." লেখা আসছে কিনা এবং কোনো এরর নেই
- ব্রাউজারে আপনার Render URL খুলুন — "✅ Telegram bot is alive and running!" লেখা দেখা উচিত
- টেলিগ্রামে গিয়ে বটকে `/start` দিন, রেসপন্স আসা উচিত

### 🔄 কোড আপডেট করলে
`bot.py` বা অন্য ফাইলে কিছু বদলালে শুধু GitHub এ নতুন করে commit করুন — Render নিজে থেকেই নতুন কোড ডিটেক্ট করে অটো রিডিপ্লয় করবে।

---

## ❓ সমস্যা হলে
- **"Unauthorized" এরর** → টোকেন ভুল, `config.py` চেক করুন
- **Admin কমান্ড কাজ করছে না** → `ADMIN_IDS`-এ আপনার আইডি ঠিকভাবে বসিয়েছেন কিনা চেক করুন
- **রেফারেল লিংক কাজ করছে না** → `BOT_USERNAME` সঠিক আছে কিনা দেখুন (@ ছাড়া)
