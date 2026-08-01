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

---

## 🔒 ফোর্স-জয়েন (বাধ্যতামূলক চ্যানেল/গ্রুপ জয়েন)

বট এখন `/start`, `/myref`, `/balance`, `/redeem`, `/app`, এবং Mini App — সবকিছুর আগে চেক করে ইউজার নির্দিষ্ট চ্যানেল/গ্রুপে জয়েন করেছে কিনা। জয়েন না করলে জয়েন-বাটন সহ মেসেজ দেখাবে।

### চ্যানেল ১ (পাবলিক — অটো ভেরিফাই হয়)
`config.py`-তে (বা Render Environment Variable এ) এগুলো বসান:
```
CHANNEL_1_TITLE = BDincomeTV
CHANNEL_1_LINK = https://t.me/BDincomeTV
CHANNEL_1_USERNAME = BDincomeTV
```
এটা কাজ করার জন্য **বটকে ওই চ্যানেলে Admin বানাতে হবে** (member list দেখার পারমিশনসহ)।

### চ্যানেল/গ্রুপ ২ (প্রাইভেট — Chat ID লাগবে)
আপনার দেওয়া `https://t.me/+ghnv_A6HgAM3Yzll-` লিংকটা একটা প্রাইভেট গ্রুপের ইনভাইট লিংক। এই ধরনের লিংকের কোনো ইউজারনেম থাকে না, তাই মেম্বারশিপ ভেরিফাই করতে numeric **Chat ID** লাগবে। ধাপগুলো:

1. বটকে ঐ গ্রুপে অ্যাড করুন এবং **Admin** বানান
2. গ্রুপে একটা মেসেজ পাঠান, সেটা **@RawDataBot** বা **@getidsbot** কে ফরওয়ার্ড করুন
3. রেসপন্সে `"chat":{"id": -100xxxxxxxxxx}` — এই নাম্বারটা কপি করুন
4. `config.py`-তে (বা Render Environment Variable এ) বসান:
```
CHANNEL_2_TITLE = আমাদের চ্যাট গ্রুপ
CHANNEL_2_LINK = https://t.me/+ghnv_A6HgAM3Yzll-
CHANNEL_2_ID = -100xxxxxxxxxx
```

> ℹ️ **আপনি বলেছিলেন সমস্যা হলে বাদ দিতে পারি** — তাই `CHANNEL_2_ID` খালি রাখলে বট শুধু চ্যানেল ১ (BDincomeTV) চেক করবে, গ্রুপটা বাদ যাবে। কোনো এরর দেখাবে না, স্বয়ংক্রিয়ভাবে স্কিপ হয়ে যাবে।

### সম্পূর্ণ বন্ধ করতে চাইলে
`/admin` প্যানেলে **Force-Join** বাটনে চাপলেই পুরো সিস্টেম অন/অফ হয়ে যাবে — কোনো কোড বদলাতে হবে না।

---

## 📱 Mini App সেটআপ (BotFather-এ Menu Button বসানো)

কোডে Mini App যুক্ত করা আছে (`static/index.html`) — সুন্দর ওয়ালেট UI, রেফারেল লিংক কপি বাটন, আর টিকিট-স্টাইল প্রোমো কোড রিডিম কার্ড। এটাকে বটের সাথে যুক্ত করতে:

1. Render-এ ডিপ্লয় হয়ে গেলে যে URL পাবেন (যেমন `https://my-telegram-bot.onrender.com`) সেটা `config.py`-তে বা Render Environment Variable-এ `MINI_APP_URL` হিসেবে বসান
2. টেলিগ্রামে **@BotFather** কে মেসেজ দিন → `/mybots` → আপনার বট সিলেক্ট করুন → **Bot Settings** → **Menu Button** → **Configure menu button**
3. URL হিসেবে আপনার Render URL দিন (যেমন `https://my-telegram-bot.onrender.com`), এবং একটা নাম দিন (যেমন `🚀 Open App`)
4. এখন বটের চ্যাটবক্সের নিচে-বামে একটা মেনু বাটন দেখাবে যেটা চাপলেই Mini App খুলবে

বটের ভেতরে `/app` কমান্ড দিলেও, বা `/start` করলে "🚀 Mini App খুলুন" বাটনেও Mini App খোলা যাবে।

---

---

## 📌 স্থায়ী "Open App" বাটন

জয়েন ভেরিফাই করার পর (বা `/start`, `/app` দিলে) বট এখন চ্যাটের **নিচে একটা স্থায়ী বাটন** পাঠায় — 🚀 **Open App**। এটা ইনলাইন বাটনের মতো মেসেজের সাথে হারিয়ে যায় না, বরং চ্যাটের নিচে কীবোর্ডের জায়গায় সবসময় লেগে থাকে, যেকোনো সময় চাপলেই Mini App খুলে যাবে।

---

## 💰 Monetag বিজ্ঞাপন দিয়ে ইনকাম (Rewarded Ad)

Mini App-এ এখন একটা **"🎬 Ad দেখুন"** ট্যাব আছে — ইউজার বিজ্ঞাপন দেখলে পয়েন্ট পাবে, আর আপনি Monetag থেকে ইনকাম করবেন। এটা Monetag এর অফিসিয়াল **Telegram Mini App SDK** ও **Server-to-Server (S2S) Postback** পদ্ধতি ব্যবহার করে বানানো — তাই কেউ জাল কল করে পয়েন্ট নিতে পারবে না, পয়েন্ট শুধু তখনই যোগ হয় যখন Monetag নিজে কনফার্ম করে যে বিজ্ঞাপনটা সত্যিই দেখানো হয়েছে ও পেমেন্ট-যোগ্য (valued)।

### ধাপ ১: Monetag অ্যাকাউন্ট ও Zone তৈরি করুন
1. **monetag.com** এ গিয়ে Publisher অ্যাকাউন্ট খুলুন
2. আপনার Telegram Mini App যুক্ত করুন (তারা bot review/moderation করতে পারে)
3. **Rewarded Interstitial** ফরম্যাটের একটা নতুন Zone তৈরি করুন
4. ড্যাশবোর্ডে **"< > Get SDK"** বাটনে ক্লিক করে স্ক্রিপ্ট ট্যাগ দেখুন, সেখান থেকে:
   - **Zone ID** (সংখ্যা, যেমন `123456`)
   - **SDK Script URL** (যেমন `https://xxxxx.com/sdk.js` — এটা অ্যাকাউন্ট-ভিত্তিক আলাদা হতে পারে)

### ধাপ ২: Render Environment Variables এ বসান
| Key | Value |
|---|---|
| `MONETAG_ZONE_ID` | আপনার Zone ID (যেমন `123456`) |
| `MONETAG_SDK_SRC` | Monetag ড্যাশবোর্ড থেকে পাওয়া SDK script URL |
| `AD_REWARD_POINTS` | একটা Ad দেখলে কত পয়েন্ট (ডিফল্ট: `5`) |
| `MONETAG_POSTBACK_SECRET` | নিজে একটা র‍্যান্ডম গোপন স্ট্রিং বানান (যেমন: `k8x2Rzq9`) |

### ধাপ ৩: Monetag ড্যাশবোর্ডে Postback URL বসান
Monetag ড্যাশবোর্ডে আপনার Zone-এর **Postback settings**-এ গিয়ে এই URL বসান (নিজের Render URL ও Secret দিয়ে বদলে নিন):
```
https://my-telegram-bot.onrender.com/api/monetag/postback?secret=k8x2Rzq9&ymid={ymid}&event={event_type}&value={reward_event_type}&telegram_id={telegram_id}
```
`{ymid}`, `{event_type}`, `{reward_event_type}`, `{telegram_id}` — এই ব্র্যাকেটসহ টেক্সটগুলো হুবহু এভাবেই বসাবেন; Monetag নিজে এগুলোকে আসল ভ্যালু দিয়ে পাল্টে দিয়ে আপনার সার্ভারে হিট করবে।

### এটা কীভাবে কাজ করে (নিরাপত্তার জন্য গুরুত্বপূর্ণ)
1. ইউজার Mini App-এ "▶️ বিজ্ঞাপন দেখুন" চাপে
2. Monetag এর বিজ্ঞাপন দেখায়, শেষ হলে ইউজারকে "ধন্যবাদ" মেসেজ দেখানো হয় (কিন্তু তখনো পয়েন্ট যোগ হয় না)
3. Monetag তাদের নিজস্ব সার্ভার থেকে (ইউজারের ব্রাউজার থেকে না) আপনার `/api/monetag/postback` URL-এ হিট করে, `reward_event_type=valued` কনফার্ম করলে তখন পয়েন্ট যোগ হয়
4. একই বিজ্ঞাপনের জন্য দুইবার পয়েন্ট যাবে না (ymid দিয়ে ডুপ্লিকেট চেক করা আছে)
5. তাই বিজ্ঞাপন দেখার কয়েক সেকেন্ড পর ব্যালেন্স আপডেট হয় — এটা বাগ না, বরং জাল ক্লিকে পয়েন্ট আটকানোর নিরাপদ ডিজাইন

> 🧪 **টেস্ট করতে**: Render এ ডিপ্লয় করার পর ব্রাউজারে গিয়ে
> `https://my-telegram-bot.onrender.com/api/monetag/postback?secret=আপনার_সিক্রেট&ymid=test1&value=valued&telegram_id=আপনার_টেলিগ্রাম_আইডি`
> ভিজিট করুন — রেসপন্সে `ok (credited)` দেখলে বুঝবেন postback ঠিকমতো কাজ করছে এবং আপনার একাউন্টে ৫ (বা যা সেট করেছেন) পয়েন্ট যোগ হয়ে গেছে।

---

## 🎨 কালার থিম
পুরো Mini App এখন **ডার্ক ব্যাকগ্রাউন্ড + অরেঞ্জ/অ্যাম্বার (yellow-orange)** থিমে — বাটন, ব্যালেন্স নাম্বার, ট্যাব হাইলাইট, টিকিট কার্ড সবকিছু এই কালার প্যালেটে মেলানো। রঙ বদলাতে চাইলে `static/index.html` ফাইলের একদম উপরে `:root { ... }` অংশে `--primary` (অরেঞ্জ) ও `--accent` (হলুদ/অ্যাম্বার) ভ্যারিয়েবল দুটো বদলালেই পুরো অ্যাপের রঙ বদলে যাবে।

---

## 🔧 কাস্টমাইজেশন
- **রেফারেল রিওয়ার্ড বদলাতে**: `config.py`-তে `REFERRAL_REWARD` বদলান
- **স্বাগতম মেসেজ বদলাতে**: `bot.py`-এর `start()` ফাংশনে টেক্সট এডিট করুন
- **Ads footer এর টেক্সট বদলাতে**: `bot.py`-এর `ads_footer()` ফাংশন দেখুন

## 📂 ফাইল স্ট্রাকচার
```
telegram_bot/
├── bot.py             ← মূল বট কোড (কমান্ড, অ্যাডমিন প্যানেল, ফোর্স-জয়েন)
├── db.py              ← শেয়ার্ড ডাটাবেজ লেয়ার (বট + Mini App দুটোই ব্যবহার করে)
├── keep_alive.py      ← Flask সার্ভার: Render কে জাগিয়ে রাখে + Mini App API
├── static/index.html  ← Mini App এর UI (ওয়ালেট, রেফার, প্রোমো রিডিম)
├── config.py          ← টোকেন, অ্যাডমিন আইডি, চ্যানেল সেটিংস ইত্যাদি
├── requirements.txt   ← প্রয়োজনীয় লাইব্রেরি
├── Procfile           ← Render স্টার্ট কমান্ড
├── .gitignore         ← যেসব ফাইল GitHub এ যাবে না
├── bot.db             ← ডাটাবেজ (প্রথমবার রান করলে অটো তৈরি হবে)
└── README.md          ← এই গাইড
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
| `MINI_APP_URL` | ডিপ্লয়ের পর Render যে URL দেবে সেটা (নিচে পাবেন — প্রথমবার খালি/অস্থায়ী রেখে পরে বসাতে পারেন) |
| `CHANNEL_1_TITLE` | `BDincomeTV` |
| `CHANNEL_1_LINK` | `https://t.me/BDincomeTV` |
| `CHANNEL_1_USERNAME` | `BDincomeTV` |
| `CHANNEL_2_TITLE` | আপনার গ্রুপের নাম |
| `CHANNEL_2_LINK` | `https://t.me/+ghnv_A6HgAM3Yzll-` |
| `CHANNEL_2_ID` | গ্রুপের numeric Chat ID (নিচে "ফোর্স-জয়েন" সেকশনে বের করার উপায় আছে; না থাকলে খালি রাখুন) |
| `MONETAG_ZONE_ID` | Monetag থেকে পাওয়া Zone ID (নিচে "Monetag" সেকশন দেখুন; না থাকলে খালি রাখুন) |
| `MONETAG_SDK_SRC` | Monetag থেকে পাওয়া SDK script URL |
| `AD_REWARD_POINTS` | `5` (চাইলে বদলান) |
| `MONETAG_POSTBACK_SECRET` | নিজের একটা গোপন র‍্যান্ডম স্ট্রিং |

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
