"""
Render.com এর Free Web Service ১৫ মিনিট নিষ্ক্রিয় থাকলে ঘুমিয়ে যায়।
এই ছোট্ট ওয়েব সার্ভারটা একটা পোর্ট খুলে রাখে, যাতে UptimeRobot প্রতি ৫ মিনিটে
এটাকে পিং করে জাগিয়ে রাখতে পারে এবং বট সবসময় চালু থাকে।
"""

import os
import threading
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "✅ Telegram bot is alive and running!"


def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()
