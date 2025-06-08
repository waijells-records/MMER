import asyncio
import json
import os
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaVideo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Константы
BOOKINGS_FILE = "bookings.json"
SERVICES_FILE = "services_full.json"
BOT_TOKEN = "7943659464:AAF-M_FGdzG57jFQf8tnD2eAzozTPC0aT7Q"
VIDEO_PATH = "intro.mp4"

# Контакты
ADMIN_CHAT_ID = "@merecords29"
NOTIFY_CHAT_ID = "@OLegKozhevin"

# Загрузка услуг
def load_services():
    with open(SERVICES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_bookings(data):
    with open(BOOKINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Стань Ближе: яркие эмоции, теплое общение и музыка, объединяющая сердца!\n\n"
        "Мечтаете о крепкой связи со своим ребёнком, а он сидит в гаджетах? Хотите создать что-то особенное, что останется с вами на всю жизнь?\n\n"
        "Представьте: вы и ваш ребёнок в профессиональной звукозаписывающей студии, вместе создаете песню и снимаете клип! Это не просто развлечение, это уникальный опыт, который укрепит вашу связь и подарит море позитивных эмоций."
    )
    if os.path.exists(VIDEO_PATH):
        await update.message.reply_video(video=open(VIDEO_PATH, 'rb'))

    await update.message.reply_text(
        "Проект 'Стань Ближе' идеально подходит для:\n"
        "• 👨‍👩‍👧 Родителей и детей-подростков\n"
        "• 💑 Пар\n"
        "• 👥 Коллективов\n\n"
        "Наши преимущества:\n"
        "• ❤️ Душевная атмосфера\n"
        "• 🎧 Проф. оборудование\n"
        "• 🎉 Удобное время\n"
        "• 🎬 Клип в подарок"
    )
    keyboard = [
        [InlineKeyboardButton("🕒 Забронировать время", callback_data="book")],
        [InlineKeyboardButton("🛒 Купить", callback_data="buy")],
        [InlineKeyboardButton("📞 Связаться", callback_data="contact")],
        [InlineKeyboardButton("📋 Услуги", callback_data="services")]
    ]
    await update.message.reply_text("Выберите действие:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    services = load_services()

    if data == "contact":
        await query.edit_message_text("📞 Связаться со студией:\nТелефон: +7 (963) 200-45-36\nTelegram: @merecords29")

    elif data == "buy":
        await query.edit_message_text(
            "💳 Способы оплаты (в разработке):\n\n"
            "• QR-код счета ИП — *скоро появится*\n"
            "• Счет ИП для перевода — *скоро появится*\n\n"
            "Пока вы можете оплатить услугу, написав нам в Telegram: @merecords29"
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
            f"Выберите время на {next_saturday.strftime('%d.%m.%Y')}",
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

        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"🔔 Новая бронь: {slot} в субботу")
        await context.bot.send_message(chat_id=NOTIFY_CHAT_ID, text=f"🔔 Новая бронь: {slot} в субботу")
        await query.edit_message_text(f"✅ Вы забронировали {slot} на {next_saturday.strftime('%d.%m.%Y')}.")

    elif data == "services":
        keyboard = [
            [InlineKeyboardButton(service["name"], callback_data=f"srv_{i}")]
            for i, service in enumerate(services)
        ]
        await query.edit_message_text("Выберите услугу:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("srv_"):
        index = int(data.split("_")[1])
        if 0 <= index < len(services):
            info = services[index]["description"]
            await query.edit_message_text(info)
        else:
            await query.edit_message_text("Информация об услуге скоро будет добавлена.")

    elif data == "none":
        await query.answer()

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    print("Бот запущен...")
    app.run_polling()
