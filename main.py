import asyncio
import json
import os
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaVideo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Файл для хранения бронирований
BOOKINGS_FILE = "bookings.json"

# 💬 Токен бота (встроенный напрямую)
BOT_TOKEN = "7943659464:AAF-M_FGdzG57jFQf8tnD2eAzozTPC0aT7Q"
VIDEO_PATH = "intro.mp4"

# Контакты для уведомлений
ADMIN_CHAT_ID = "@merecords29"
NOTIFY_CHAT_ID = "@OLegKozhevin"

# --- Загрузка и сохранение данных ---
def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_bookings(data):
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# --- Генерация слотов ---
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

# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Стань Ближе: яркие эмоции, теплое общение и музыка, объединяющая сердца!\n\n"
        "Мечтаете о крепкой связи со своим ребёнком, а он сидит в гаджетах?\n"
        "Хотите создать нечто особенное, что останется с вами на всю жизнь?\n\n"
        "Представьте: вы и ваш ребёнок в профессиональной студии, записываете песню, а потом снимаете клип! "
        "Это не просто развлечение, а настоящий совместный опыт."
    )

    if os.path.exists(VIDEO_PATH):
        await update.message.reply_video(video=open(VIDEO_PATH, 'rb'))

    await update.message.reply_text(
        "Проект «Стань Ближе» идеально подойдёт для:\n"
        "• 👨‍👩‍👧 Родителей и детей\n"
        "• 💑 Пар\n"
        "• 👥 Коллективов"
    )
    await update.message.reply_text(
        "Наши преимущества:\n"
        "• ❤️ Незабываемые эмоции\n"
        "• 🎧 Проф. оборудование\n"
        "• 🎉 Удобное время\n"
        "• 🎬 Клип на память"
    )

    keyboard = [
        [InlineKeyboardButton("🕒 Забронировать", callback_data="book")],
        [InlineKeyboardButton("🛒 Купить", callback_data="buy")],
        [InlineKeyboardButton("📞 Связаться", callback_data="contact")],
        [InlineKeyboardButton("🎵 Услуги студии", callback_data="services")]
    ]
    await update.message.reply_text("Выберите действие:", reply_markup=InlineKeyboardMarkup(keyboard))

# --- Обработка кнопок ---
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "contact":
        await query.edit_message_text("📞 Связаться со студией:\nТелефон: +7 (963) 200-45-36\nTelegram: @merecords29")

    elif data == "buy":
        await query.edit_message_text(
            "💳 Оплата вручную. Напишите нам @merecords29.\n"
            "Позже появится Telegram Pay.\n"
            "Выберите способ оплаты:\n"
            "1. Перевод на карту\n"
            "2. Оплата через Telegram Pay\n"
            "3. QR-код"
        )

    elif data == "book":
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
            await query.edit_message_text("Это время уже занято.")
            return
        booked_slots.append(slot)
        bookings[date_str] = booked_slots
        save_bookings(bookings)

        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"🔔 Бронь: {slot} в субботу")
        await context.bot.send_message(chat_id=NOTIFY_CHAT_ID, text=f"🔔 Бронь: {slot} в субботу")
        await query.edit_message_text(f"✅ Вы забронировали {slot} на {next_saturday.strftime('%d.%m.%Y')}.")

    elif data == "services":
        keyboard = [
            [InlineKeyboardButton("1️⃣ Аудиосказка", callback_data="service_1")],
            [InlineKeyboardButton("2️⃣ Запись вокала", callback_data="service_2")],
            [InlineKeyboardButton("3️⃣ Сведение", callback_data="service_3")],
            [InlineKeyboardButton("4️⃣ Дистрибуция", callback_data="service_4")],
            [InlineKeyboardButton("5️⃣ Песня под ключ", callback_data="service_5")],
            [InlineKeyboardButton("6️⃣ Сертификат", callback_data="service_6")],
            [InlineKeyboardButton("7️⃣ Инструментал", callback_data="service_7")],
            [InlineKeyboardButton("8️⃣ Обложка/Сторис", callback_data="service_8")],
            [InlineKeyboardButton("9️⃣ Клип", callback_data="service_9")],
            [InlineKeyboardButton("🔟 Озвучка", callback_data="service_10")],
            [InlineKeyboardButton("1️⃣1️⃣ Подкаст", callback_data="service_11")],
            [InlineKeyboardButton("1️⃣2️⃣ Оцифровка", callback_data="service_12")],
            [InlineKeyboardButton("1️⃣3️⃣ Мастер-класс", callback_data="service_13")],
            [InlineKeyboardButton("1️⃣4️⃣ Звук на съёмке", callback_data="service_14")],
        ]
        await query.edit_message_text("Выберите услугу:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("service_"):
        idx = int(data.split("_")[1])
        with open("services.json", "r", encoding="utf-8") as f:
            all_services = json.load(f)
        info = all_services.get(str(idx), "Информация не найдена.")
        keyboard = [
            [InlineKeyboardButton("🕒 Забронировать", callback_data="book")],
            [InlineKeyboardButton("🛒 Купить", callback_data="buy")],
            [InlineKeyboardButton("🔙 Назад", callback_data="services")]
        ]
        await query.edit_message_text(info, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "none":
        await query.answer("Это время недоступно.", show_alert=True)

# --- Запуск бота ---
if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))

    print("✅ Бот запущен...")
    app.run_polling()
