import telebot
import json
import os
import random
import time
from telebot import types

TOKEN = '8232952137:AAE9dGtnUygKXWqJhdgqmETXArFzeql9pxI'
bot = telebot.TeleBot(TOKEN)
DATA_FILE = 'persik_ultra_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "phrases": ["всем привет", "я могу иногда башкой ударится"],
        "photos": [], "stickers": [], "triggers": {},
        "blacklist": ["кринж", "плохой"],
        "reactions": ["🔥", "😭", "🌚", "💀", "🍑"],
        "chance": 0.3, "typing_speed": 1, 
        "mute_mode": False, "auto_reaction": True
    }

data = load_data()
user_state = {}

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def ultra_menu(page=1):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if page == 1:
        markup.add(
            types.InlineKeyboardButton("📝 +Фраза", callback_data="add_txt"),
            types.InlineKeyboardButton("🎯 +Триггер", callback_data="add_trig"),
            types.InlineKeyboardButton("🃏 +Стикер", callback_data="add_stik"),
            types.InlineKeyboardButton("🎲 Шанс: " + str(data.get('chance', 0.3)), callback_data="set_chance"),
            types.InlineKeyboardButton("➡️ Далее", callback_data="page_2")
        )
    else:
        m_st = "🔇 ВКЛ" if data.get('mute_mode') else "🔊 ВЫКЛ"
        markup.add(
            types.InlineKeyboardButton(f"Тишина: {m_st}", callback_data="toggle_mute"),
            types.InlineKeyboardButton("🔥 Реакции", callback_data="toggle_reac"),
            types.InlineKeyboardButton("🧹 Очистить", callback_data="clear_phrases"),
            types.InlineKeyboardButton("⬅️ Назад", callback_data="page_1"),
            types.InlineKeyboardButton("📊 Стата", callback_data="stat")
        )
    return markup

@bot.message_handler(func=lambda m: m.text == "settings27728284948")
def open_settings(message):
    bot.send_message(message.chat.id, "🐾 **SUPREME CONFIG**", reply_markup=ultra_menu(1), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid = call.message.chat.id
    if call.data == "page_1": bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=ultra_menu(1))
    elif call.data == "page_2": bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=ultra_menu(2))
    elif call.data == "add_txt":
        user_state[cid] = 'wait_txt'
        bot.send_message(cid, "✍️ Пиши фразу:")
    elif call.data == "add_trig":
        user_state[cid] = 'wait_trig_k'
        bot.send_message(cid, "🎯 На какое слово реагировать?")
    elif call.data == "add_stik":
        user_state[cid] = 'wait_stik'
        bot.send_message(cid, "🃏 Пришли стикер!")
    elif call.data == "set_chance":
        data['chance'] = round((data.get('chance', 0.3) + 0.1) if data.get('chance', 0.3) < 1.0 else 0.0, 1)
        save_data()
        bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=ultra_menu(1))
    elif call.data == "stat":
        bot.answer_callback_query(call.id, f"Фраз: {len(data['phrases'])}\nСтикеров: {len(data['stickers'])}\nТриггеров: {len(data['triggers'])}", show_alert=True)

@bot.message_handler(content_types=['text', 'sticker', 'photo'])
def handle_messages(message):
    cid = message.chat.id
    
    # ПРОВЕРКА СОСТОЯНИЙ (НАСТРОЙКИ)
    if cid in user_state:
        state = user_state[cid]
        if state == 'wait_txt' and message.text:
            data["phrases"].append(message.text)
            save_data(); del user_state[cid]
            bot.send_message(cid, "✅ Фраза добавлена!")
        elif state == 'wait_stik' and message.content_type == 'sticker':
            data["stickers"].append(message.sticker.file_id)
            save_data(); del user_state[cid]
            bot.send_message(cid, "✅ Стикер в базе!")
        elif state == 'wait_trig_k' and message.text:
            user_state[cid] = f"wait_trig_v:{message.text.lower()}"
            bot.send_message(cid, f"🎯 Что ответить на '{message.text}'?")
        elif state.startswith('wait_trig_v:') and message.text:
            key = state.split(':')[1]
            data["triggers"][key] = message.text
            save_data(); del user_state[cid]
            bot.send_message(cid, f"✅ Триггер '{key}' готов!")
        return

    # ОБЫЧНАЯ ЛОГИКА
    if data.get('mute_mode'): return
    
    text = message.text.lower() if message.text else ""
    
    # Реакции
    if data.get('auto_reaction') and random.random() < 0.2:
        try: bot.set_message_reaction(cid, message.message_id, [types.ReactionTypeEmoji(random.choice(data["reactions"]))])
        except: pass

    # Проверка триггеров
    for key, val in data["triggers"].items():
        if key in text:
            bot.reply_to(message, val)
            return

    # Случайный ответ
    if random.random() < data.get('chance', 0.3):
        choice = random.choice(['text', 'sticker']) if data["stickers"] else 'text'
        if choice == 'sticker': bot.send_sticker(cid, random.choice(data["stickers"]))
        else: bot.send_message(cid, random.choice(data["phrases"]))

print("ПЕРСИК SUPREME READY")
bot.polling(none_stop=True, skip_pending=True)
