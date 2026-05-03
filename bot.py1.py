import telebot
from telebot import types
import requests
import random
import os
import json
import re

# --- কনফিগারেশন ---
API_TOKEN = '7926833731:AAFw1ilR7woSoYIo3CM2bCO5_ybXLEvCkRE'
ADMIN_ID = 8254642168 
bot = telebot.TeleBot(API_TOKEN)
DB_FILE = "users.json"

# --- ডাটাবেস ফাংশন ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- ফ্রি ইমেইল এবং ওটিপি ফাংশন ---
def get_free_email():
    domains = ["1secmail.com", "1secmail.org", "1secmail.net"]
    username = f"user{random.randint(1000, 9999)}"
    domain = random.choice(domains)
    email = f"{username}@{domain}"
    password = f"Pass@{random.randint(1000, 9999)}"
    return email, username, domain, password

def get_otp(username, domain):
    url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}"
    try:
        response = requests.get(url).json()
        if response:
            msg_id = response[0]['id']
            msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={msg_id}"
            msg_content = requests.get(msg_url).json()
            code = re.findall(r'\b\d{6}\b', msg_content['body'])
            return code[0] if code else "কোড এখনো আসেনি"
    except:
        pass
    return None

# --- কিবোর্ড মেনু ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🧾 কাজ ▶️', '💵 ব্যালেন্স', '🏦 টাকা উত্তোলন', '🎁 Invite & Earn', '☎️ সাপোর্ট', '🎯 মিশন')
    return markup

# --- স্টার্ট কমান্ড ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    data = load_data()
    if user_id not in data:
        params = message.text.split()
        referrer = params[1] if len(params) > 1 and params[1] != user_id else None
        data[user_id] = {"balance": 0.0, "referred_by": referrer, "done_first": False, "total_work": 0}
        save_data(data)
    bot.send_message(message.chat.id, f"👋 স্বাগতম {message.from_user.first_name}!", reply_markup=main_menu())

# --- মেইন বাটন হ্যান্ডলার ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = str(message.chat.id)
    data = load_data()
    if user_id not in data: return

    if message.text == '💵 ব্যালেন্স':
        bal = data[user_id].get("balance", 0.0)
        bot.send_message(message.chat.id, f"💰 আপনার ব্যালেন্স: {bal:.2f} টাকা")

    elif message.text == '🎁 Invite & Earn':
        bot_user = bot.get_me().username
        link = f"https://t.me/{bot_user}?start={user_id}"
        bot.send_message(message.chat.id, f"🎁 আপনার রেফার লিংক:\n{link}")

    elif message.text == '🏦 টাকা উত্তোলন':
        bal = data[user_id].get("balance", 0.0)
        if bal >= 50:
            bot.send_message(message.chat.id, "🏦 উইথড্র দিতে অ্যাডমিনকে নক দিন: @Tanjim_Admin")
        else:
            bot.send_message(message.chat.id, f"⚠️ কমপক্ষে ৫০ টাকা লাগবে। আপনার আছে {bal:.2f} টাকা।")

    elif message.text == '🎯 মিশন':
        work = data[user_id].get("total_work", 0)
        bot.send_message(message.chat.id, f"🎯 আজ আপনি {work}টি কাজ করেছেন।")

    elif message.text == '☎️ সাপোর্ট':
        bot.send_message(message.chat.id, "🆘 যোগাযোগ: @Tanjim_Admin")

    elif message.text == '🧾 কাজ ▶️':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("ইন্সটাগ্রাম (৳২.৫০)", callback_data="start_task"))
        bot.send_message(message.chat.id, "⬇️ কাজ শুরু করতে চাপুন:", reply_markup=markup)

# --- ইনলাইন বাটন হ্যান্ডলার ---
@bot.callback_query_handler(func=lambda call: True)
def callback_logic(call):
    user_id = str(call.message.chat.id)
    data = load_data()