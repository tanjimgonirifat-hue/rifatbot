import telebot
from telebot import types
import os
import json
from flask import Flask
from threading import Thread

# --- ১. ওয়েব সার্ভার (বটকে ২৪ ঘণ্টা সচল রাখার জন্য) ---
app = Flask('')

@app.route('/')
def home():
    return "বট বর্তমানে অনলাইনে আছে!"

def run():
    # Render বা Koyeb এই পোর্টের মাধ্যমে সার্ভার কানেক্ট করে
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- ২. বটের তথ্য ও ডাটাবেস ---
API_TOKEN = '7926833731:AAFw1ilR7woSoYIo3CM2bCO5_ybXLEvCkRE'
bot = telebot.TeleBot(API_TOKEN)
DB_FILE = "users.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- ৩. মেইন কিবোর্ড মেনু (যা স্টার্ট দিলে নিচে আসবে) ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton('🧾 কাজ ▶️'),
        types.KeyboardButton('💵 ব্যালেন্স'),
        types.KeyboardButton('🏦 টাকা উত্তোলন'),
        types.KeyboardButton('🎁 Invite & Earn'),
        types.KeyboardButton('🎯 মিশন'),
        types.KeyboardButton('☎️ সাপোর্ট')
    )
    return markup

# --- ৪. স্টার্ট কমান্ড ---
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)
    user_db = load_data()
    
    if chat_id not in user_db:
        user_db[chat_id] = {"balance": 0.0, "total_work": 0}
        save_data(user_db)
    
    welcome_text = (f"👋 স্বাগতম {message.from_user.first_name}!\n"
                    "আমাদের প্রফেশনাল আর্নিং বটে আপনাকে স্বাগতম।\n"
                    "নিচের মেনু ব্যবহার করে আপনার কাজ শুরু করুন।")
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

# --- ৫. বাটন ক্লিক হ্যান্ডলার ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    chat_id = str(message.chat.id)
    user_db = load_data()

    if message.text == '💵 ব্যালেন্স':
        bal = user_db.get(chat_id, {}).get("balance", 0.0)
        bot.send_message(message.chat.id, f"💰 আপনার বর্তমান ব্যালেন্স: {bal:.2f} টাকা")

    elif message.text == '🧾 কাজ ▶️':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔥 কাজ শুরু করুন", callback_data="do_work"))
        bot.send_message(message.chat.id, "⬇️ কাজ জমা দিতে নিচের বাটনে ক্লিক করুন:", reply_markup=markup)

    elif message.text == '☎️ সাপোর্ট':
        bot.send_message(message.chat.id, "🆘 যেকোনো প্রয়োজনে যোগাযোগ করুন: @Tanjim_Admin")

# --- ৬. কাজ সম্পন্ন করার লজিক ---
@bot.callback_query_handler(func=lambda call: True)
def callback_logic(call):
    chat_id = str(call.message.chat.id)
    user_db = load_data()

    if call.data == "do_work":
        user_db[chat_id]["balance"] += 2.50
        user_db[chat_id]["total_work"] += 1
        save_data(user_db)
        bot.answer_callback_query(call.id, "✅ টাকা যোগ হয়েছে!")
        bot.edit_message_text("🎉 কাজ সফল! ২.৫০ টাকা আপনার ব্যালেন্সে যোগ করা হয়েছে।", call.message.chat.id, call.message.message_id)

# --- ৭. রান পয়েন্ট ---
if name == "main":
    print("বটটি এখন লাইভ হচ্ছে...")
    keep_alive() 
    bot.infinity_polling()
