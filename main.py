import telebot
import json
import os
import random
import time
from telebot import types

TOKEN = '8484621573:AAGjGx6j5jYGLUlotDTB3ay3sAn3NsAhAKI'
bot = telebot.TeleBot(TOKEN)
DATA_FILE = 'persik_ultra_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "phrases": ["ну привет всем", "жрать"],
        "photos": [], "stickers": [], "triggers": {},
        "blacklist": ["кринж", "плохой"],
        "reactions": ["🔥", "👍", "🐾", "😎", "😱"],
        "interval": 30, "last_chat_id": None
    }

data = load_data()
user_state = {}

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def ultra_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📝 Новая фраза", callback_data="add_txt"),
        types.InlineKeyboardButton("🎯 Триггер", callback_data="add_trig"),
        types.InlineKeyboardButton("🃏 База Стикеров", callback_data="add_stik"),
        types.InlineKeyboardButton("📊 Инфо", callback_data="stat")
    )
    return markup

@bot.message_handler(func=lambda m: m.text == "settings27728284948")
def open_settings(message):
    bot.send_message(message.chat.id, "🐾 **PERSIK ULTRA CONFIG**\nДен, настройки готовы к бою:",
                     reply_markup=ultra_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid = call.message.chat.id
    if call.data == "add_txt":
        user_state[cid] = 'wait_txt'
        bot.send_message(cid, "✍️ Напиши фразу:")
    elif call.data == "add_trig":
        user_state[cid] = 'wait_trig_k'
        bot.send_message(cid, "🎯 На какое слово реагировать?")
    elif call.data == "add_stik":
        user_state[cid] = 'wait_stik'
        bot.send_message(cid, "🃏 Отправь стикер!")
    elif call.data == "stat":
        bot.answer_callback_query(call.id, f"Фраз: {len(data['phrases'])}\nТриггеров: {len(data['triggers'])}\nСтикеров: {len(data['stickers'])}", show_alert=True)

@bot.message_handler(content_types=['text', 'photo', 'sticker'])
def handle_all(message):
    cid = message.chat.id
    text = message.text.lower() if message.text else ""

    if text == "new8226":
        user_state[cid] = 'wait_txt'
        bot.send_message(cid, "🔧 Быстрое обучение!")
        return

    if cid in user_state:
        state = user_state[cid]
        if state == 'wait_txt' and message.text:
            data["phrases"].append(message.text)
            save_data(); del user_state[cid]
            bot.send_message(cid, "✅ Выучил!")
        elif state == 'wait_stik' and message.content_type == 'sticker':
            data["stickers"].append(message.sticker.file_id)
            save_data(); del user_state[cid]
            bot.send_message(cid, "✅ Стикер в базе!")
        elif state == 'wait_trig_k':
            user_state[cid] = f'wait_trig_v:{text}'
            bot.send_message(cid, f"🎯 Что ответить на '{text}'?")
        elif state.startswith('wait_trig_v:'):
            key = state.split(':')[1]
            data["triggers"][key] = message.text
            save_data(); del user_state[cid]
            bot.send_message(cid, "✅ Триггер установлен!")
        return

    for bad_word in data["blacklist"]:
        if bad_word in text:
            bot.reply_to(message, "Фу, не пиши такое")
            return

    for key, val in data["triggers"].items():
        if key in text:
            bot.send_chat_action(cid, 'typing')
            time.sleep(1)
            bot.reply_to(message, val)
            return

    chance = 1.0 if message.chat.type == 'private' else 0.3
    if random.random() < chance:
        bot.send_chat_action(cid, 'typing')
        time.sleep(random.uniform(1, 3))
        choice = random.choice(['text', 'photo', 'sticker'])
        if choice == 'sticker' and data["stickers"]:
            bot.send_sticker(cid, random.choice(data["stickers"]))
        elif choice == 'photo' and data["photos"]:
            bot.send_photo(cid, random.choice(data["photos"]))
        elif data["phrases"]:
            bot.send_message(cid, random.choice(data["phrases"]))

print("ПЕРСИК ЗАПУЩЕН!")
bot.polling(none_stop=True)
