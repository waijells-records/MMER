# main.py — основной код Telegram-бота проекта "Стань Ближе"
# Используется python-telegram-bot v20+, async, json для хранения данных

import asyncio
import json
import os
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaVideo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Путь к JSON-файлу для хранения данных о бронированиях
BOOKINGS_FILE = "bookings.json"

# Токен Telegram-бота
BOT_TOKEN = os.getenv("BOT_TOKEN") or "ВАШ_ТОКЕН_ЗДЕСЬ"
VIDEO_PATH = "intro.mp4"

# Контакты
ADMIN_CHAT_ID = "@merecords29"
NOTIFY_CHAT_ID = "@OLegKozhevin"

# Список всех 14 услуг
services = {
    "record_fairy": "\u2728 Запись аудиосказки\n6 000 \u20bd\n\n- 1 час студии\n- Обработка\n- Саунд-дизайн\n...",
    "record_vocal": "\ud83d\udd34 Запись вокала\n1 000 \u20bd/час\n...",
    "mixing": "\u2705 Сведение\nSTANDART от 4 000 \u20bd\nPRO от 5 000 \u20bd\n...",
    "distribution": "\u2709\ufe0f Дистрибуция\nСингл — 1 000 \u20bd\nEP — 1 700 \u20bd\n...",
    "song_full": "\ud83c\udfb5 Песня под ключ\nот 20 000 \u20bd\n...",
    "gift_card": "\ud83c\udff7\ufe0f Подарочный сертификат\nот 2 000 до 25 000 \u20bd\n...",
    "instrumental": "\ud83d\udcfc Создание инструментала\nот 10 000 \u20bd\n...",
    "cover_story": "\ud83d\udcf7 Обложка / Сторис\nОбложка — от 1 500 \u20bd\n...",
    "clip": "\ud83c\udfa5 Создание клипа\nот 80 000 \u20bd\n...",
    "voiceover": "\ud83c\udfa7 Озвучка\nот 2 000 \u20bd / минута\n...",
    "podcast": "\ud83c\udf99\ufe0f Подкаст\nКомплекс — от 9 000 \u20bd\n...",
    "digitizing": "\ud83d\udcfc Оцифровка\nVHS — от 1 000 \u20bd\n...",
    "masterclass": "\ud83d\udd27 Мастер-класс\n2 500 \u20bd\n...",
    "onset_record": "\ud83c\udf04 Звук на площадке\nот 8 000 \u20bd\n..."
}

# Вспомогательные функции

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_bookings(data):
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def generate_slots(date, is_stan_blizhe=False):
    start = 10
    end = 22
    slots = []
    delta = timedelta(minutes=90 if is_stan_blizhe else 60)
    pause = timedelta(minutes=30 if is_stan_blizhe else 0)
    now = datetime.combine(date, datetime.min.time()).replace(hour=start)
    while now.hour < end:
        slots.append(now.strftime("%H:%M"))
        now += delta + pause
    return slots

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "\ud83c\udfa5 Стань Ближе: яркие эмоции, теплое общение и музыка, объединяющая сердца!\n\nМечтаете о крепкой связи со своим ребёнком, а он сидит в гаджетах? Хотите создать нечто особенное, что останется с вами на всю жизнь?\n\nПредставьте: вы и ваш ребёнок в профессиональной студии, записываете песню, а потом снимаете клип! Это не просто развлечение, а настоящий совместный опыт."
    )
    if os.path.exists(VIDEO_PATH):
        await update.message.reply_video(video=open(VIDEO_PATH, 'rb'))

    await update.message.reply_text(
        "Проект идеально подойдёт для:\n• \ud83d\udc68\u200d\ud83d\udc69\u200d\ud83d\udc67 Родителей и детей\n• \ud83d\udc91 Пар\n• \ud83d\udc65 Коллективов\n\nНаши преимущества:\n• \u2764\ufe0f Тёплая атмосфера\n• \ud83c\udfa7 Крутой звук\n• \ud83c\udf89 Удобное время\n• \ud83c\udfa5 Клип на память"
    )

    keyboard = [
        [InlineKeyboardButton("\ud83d\udd52 Забронировать время", callback_data="book")],
        [InlineKeyboardButton("\ud83d\udcb2 Купить", callback_data="buy")],
        [InlineKeyboardButton("\ud83d\udcde Связаться", callback_data="contact")],
        [InlineKeyboardButton("\ud83d\udcc5 Услуги студии", callback_data="services")]
    ]
    await update.message.reply_text("Выберите действие:", reply_markup=InlineKeyboardMarkup(keyboard))

# Кнопки
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "contact":
        await query.edit_message_text("Связаться со студией:\nТелефон: +7 (963) 200-45-36\nTelegram: @merecords29")

    elif data == "buy":
        await query.edit_message_text("Оплата временно вручную. Напишите нам: @merecords29")

    elif data == "services":
        keyboard = [[InlineKeyboardButton(title, callback_data=key)] for key, title in zip(services.keys(), services.values())]
        keyboard.append([InlineKeyboardButton("\u2b05\ufe0f Назад", callback_data="back")])
        await query.edit_message_text("\ud83c\udcc5 Услуги студии:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "book":
        today = datetime.now()
        next_saturday = today + timedelta((5 - today.weekday()) % 7)
        slots = generate_slots(next_saturday.date(), is_stan_blizhe=True)
        bookings = load_bookings().get(next_saturday.strftime("%Y-%m-%d"), [])

        keyboard = []
        for slot in slots:
            if slot in bookings:
                keyboard.append([InlineKeyboardButton(f"\u274c {slot} (занято)", callback_data="none")])
            else:
                keyboard.append([InlineKeyboardButton(f"\ud83d\udfe2 {slot}", callback_data=f"book_{slot}")])

        await query.edit_message_text(
            f"Выберите время на {next_saturday.strftime('%d.%m.%Y')}:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("book_"):
        slot = data.split("_")[1]
        today = datetime.now()
        next_saturday = today + timedelta((5 - today.weekday()) % 7)
        date_str = next_saturday.strftime("%Y-%m-%d")

        bookings = load_bookings()
        booked_slots = bookings.get(date_str, [])
        if slot in booked_slots:
            await query.edit_message_text("Это время уже занято. Выберите другое.")
            return
        booked_slots.append(slot)
        bookings[date_str] = booked_slots
        save_bookings(bookings)

        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"\ud83d\udd14 Новая бронь: {slot} в субботу")
        await context.bot.send_message(chat_id=NOTIFY_CHAT_ID, text=f"\ud83d\udd14 Новая бронь: {slot} в субботу")

        await query.edit_message_text(f"\u2705 Вы забронировали время {slot} на {next_saturday.strftime('%d.%m.%Y')}.")

    elif data in services:
        text = services[data]
        keyboard = [
            [InlineKeyboardButton("\ud83d\udd52 Забронировать", callback_data="book")],
            [InlineKeyboardButton("\ud83d\udcb2 Купить", callback_data="buy")],
            [InlineKeyboardButton("\ud83d\udcde Связаться", callback_data="contact")],
            [InlineKeyboardButton("\u2b05\ufe0f Назад", callback_data="services")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "back":
        await start(update, context)

async def ignore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

# Запуск
if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(CallbackQueryHandler(ignore, pattern="^none$"))
    print("\u2705 Бот запущен...")
    app.run_polling()
