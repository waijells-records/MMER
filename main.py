# Основной скелет Telegram-бота для студии "Стань Ближе"
# Использует python-telegram-bot v20+, asyncio, и json-файл как "базу данных"

import asyncio
import json
import os
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaVideo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Путь к JSON-файлу для хранения данных о бронированиях
BOOKINGS_FILE = "bookings.json"

# Загрузка токена и путей
BOT_TOKEN = os.getenv("BOT_TOKEN") or "ВАШ_ТОКЕН_ЗДЕСЬ"
VIDEO_PATH = "intro.mp4"

# Контакты
ADMIN_CHAT_ID = "@merecords29"
NOTIFY_CHAT_ID = "@OLegKozhevin"

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
        slot = now.strftime("%H:%M")
        slots.append(slot)
        now += delta + pause
    return slots

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Стань Ближе: яркие эмоции, теплое общение и музыка, объединяющая сердца!\n\n"
        "Мечтаете о крепкой связи со своим ребенком, а он сидит в гаджетах? Хотите создать что-то особенное, что останется с вами на всю жизнь?\n\n"
        "Представьте: вы и ваш ребенок в профессиональной студии, вместе создаете песню и снимаете клип! Это уникальный опыт, который укрепит вашу связь."
    )
    if os.path.exists(VIDEO_PATH):
        await update.message.reply_video(video=open(VIDEO_PATH, 'rb'))

    keyboard = [[InlineKeyboardButton("🕒 Забронировать время", callback_data="book")],
                [InlineKeyboardButton("🛒 Купить", callback_data="buy")],
                [InlineKeyboardButton("📞 Связаться", callback_data="contact")]]
    await update.message.reply_text("Выберите действие:", reply_markup=InlineKeyboardMarkup(keyboard))

# Обработка нажатий на кнопки
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "contact":
        await query.edit_message_text(
            "Связаться со студией:\n"
            "Телефон: +7 (963) 200-45-36\n"
            "Telegram: @merecords29"
        )

    elif data == "buy":
        await query.edit_message_text(
            "Оплата временно осуществляется вручную.\n\n"
            "После выбора услуги напишите нам: @merecords29\n\n"
            "(В будущем появится возможность оплатить через Telegram Pay)"
        )

    elif data == "book":
        # Пример отображения слотов на ближайшую субботу (Стань Ближе)
        today = datetime.now()
        next_saturday = today + timedelta((5 - today.weekday()) % 7)
        slots = generate_slots(next_saturday.date(), is_stan_blizhe=True)
        bookings = load_bookings().get(next_saturday.strftime("%Y-%m-%d"), [])

        keyboard = []
        for slot in slots:
            if slot in bookings:
                keyboard.append([InlineKeyboardButton(f"❌ {slot} (занято)", callback_data="none")])
            else:
                keyboard.append([InlineKeyboardButton(f"🟢 {slot}", callback_data=f"book_{slot}")])

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
            await query.edit_message_text("Это время уже занято. Пожалуйста, выберите другое.")
            return
        booked_slots.append(slot)
        bookings[date_str] = booked_slots
        save_bookings(bookings)

        # Уведомление администраторам
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"🔔 Новая бронь: {slot} в субботу")
        await context.bot.send_message(chat_id=NOTIFY_CHAT_ID, text=f"🔔 Новая бронь: {slot} в субботу")

        await query.edit_message_text(f"✅ Вы забронировали время {slot} на {next_saturday.strftime('%d.%m.%Y')}. До встречи в студии!")

# Заглушка на неиспользуемую кнопку
async def ignore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

# Запуск бота
if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(CallbackQueryHandler(ignore, pattern="^none$"))

    print("Бот запущен...")
    app.run_polling()
