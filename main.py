import telebot
import json
import os
import random
import time
from telebot import types

# Ден, твой токен подхватится сам
TOKEN = '8484621573:AAGjGx6j5jYGLUlotDTB3ay3sAn3NsAhAKI'
bot = telebot.TeleBot(TOKEN)
DATA_FILE = 'persik_ultra_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "phrases": ["всем привет", "жрать"],
        "photos": [], 
        "stickers": [], 
        "triggers": {},
        "blacklist": ["кринж", "плохой"],
        "reactions": ["🔥", "👍", "🐾", "😎", "😱"],
        "chance": 0.3, # Шанс ответа (0.0 - 1.0)
        "typing_speed": 2, # Секунды имитации печати
        "mute_mode": False, # Режим тишины
        "ai_logic": True, # Имитация логики
        "auto_reaction": True # Ставить ли реакции на сообщения
    }

data = load_data()
user_state = {}

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ГЕНЕРАТОР ГИГАНТСКОГО МЕНЮ
def ultra_menu(page=1):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if page == 1:
        markup.add(
            types.InlineKeyboardButton("📝 Добавить фразу", callback_data="add_txt"),
            types.InlineKeyboardButton("🎯 Новый триггер", callback_data="add_trig"),
            types.InlineKeyboardButton("🃏 База стикеров", callback_data="add_stik"),
            types.InlineKeyboardButton("🎲 Шанс: " + str(data.get('chance', 0.3)), callback_data="set_chance"),
            types.InlineKeyboardButton("➡️ Далее", callback_data="page_2")
        )
    elif page == 2:
        mute_status = "🔇 ВКЛ" if data.get('mute_mode') else "🔊 ВЫКЛ"
        ai_status = "🧠 ИИ: ВКЛ" if data.get('ai_logic') else "🧠 ИИ: ВЫКЛ"
        markup.add(
            types.InlineKeyboardButton(f"Режим тишины: {mute_status}", callback_data="toggle_mute"),
            types.InlineKeyboardButton(ai_status, callback_data="toggle_ai"),
            types.InlineKeyboardButton("🔥 Авто-реакции", callback_data="toggle_reac"),
            types.InlineKeyboardButton("🧹 Очистить фразы", callback_data="clear_phrases"),
            types.InlineKeyboardButton("⬅️ Назад", callback_data="page_1"),
            types.InlineKeyboardButton("📊 Статистика", callback_data="stat")
        )
    return markup

@bot.message_handler(func=lambda m: m.text == "settings27728284948")
def open_settings(message):
    bot.send_message(message.chat.id, "👑 **PERSIK SUPREME CONFIG**\nДен, тут управление миром:",
                     reply_markup=ultra_menu(1), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid = call.message.chat.id
    
    # Навигация
    if call.data == "page_1":
        bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=ultra_menu(1))
    elif call.data == "page_2":
        bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=ultra_menu(2))
    
    # Функции
    elif call.data == "add_txt":
        user_state[cid] = 'wait_txt'
        bot.send_message(cid, "✍️ Какую фразу выучить?")
    elif call.data == "toggle_mute":
        data['mute_mode'] = not data.get('mute_mode', False)
        save_data()
        bot.answer_callback_query(call.id, "Режим тишины изменен!")
        bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=ultra_menu(2))
    elif call.data == "set_chance":
        data['chance'] = round((data.get('chance', 0.3) + 0.1) % 1.1, 1)
        save_data()
        bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=ultra_menu(1))
    elif call.data == "stat":
        msg = (f"📈 **СТАТИСТИКА**\n"
               f"• Фраз: {len(data['phrases'])}\n"
               f"• Триггеров: {len(data['triggers'])}\n"
               f"• Стикеров: {len(data['stickers'])}\n"
               f"• Шанс ответа: {data.get('chance')*100}%")
        bot.send_message(cid, msg, parse_mode="Markdown")

@bot.message_handler(content_types=['text', 'photo', 'sticker'])
def handle_all(message):
    cid = message.chat.id
    if data.get('mute_mode') and message.text != "settings27728284948":
        return

    # Состояния (обучение)
    if cid in user_state:
        state = user_state[cid]
        if state == 'wait_txt' and message.text:
            data["phrases"].append(message.text)
            save_data(); del user_state[cid]
            bot.send_message(cid, "✅ Запомнил!")
            return

    # Авто-реакции (если включены)
    if data.get('auto_reaction') and random.random() < 0.2:
        try:
            bot.set_message_reaction(cid, message.message_id, [types.ReactionTypeEmoji(random.choice(data["reactions"]))])
        except: pass

    # Логика ответов
    text = message.text.lower() if message.text else ""
    
    # Проверка триггеров
    for key, val in data["triggers"].items():
        if key in text:
            bot.send_chat_action(cid, 'typing')
            time.sleep(data.get('typing_speed', 1))
            bot.reply_to(message, val)
            return

    # Случайный ответ
    if random.random() < data.get('chance', 0.3):
        bot.send_chat_action(cid, 'typing')
        time.sleep(random.uniform(1, 3))
        
        pool = []
        if data["phrases"]: pool.extend(['text'] * 5)
        if data["stickers"]: pool.extend(['sticker'] * 2)
        
        if not pool: return
        
        choice = random.choice(pool)
        if choice == 'sticker':
            bot.send_sticker(cid, random.choice(data["stickers"]))
        else:
            bot.send_message(cid, random.choice(data["phrases"]))

print("ПЕРСИК SUPREME ЗАПУЩЕН!")
# skip_pending=True чтобы не спамил старым!
bot.polling(none_stop=True, skip_pending=True)
