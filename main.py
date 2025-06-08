from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import json
import logging

API_TOKEN = '7943659464:AAF-M_FGdzG57jFQf8tnD2eAzozTPC0aT7Q'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

with open("services_full.json", encoding='utf-8') as f:
    SERVICES = json.load(f)

main_kb = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("🎬 Забронировать время", callback_data="book_time"),
    InlineKeyboardButton("📞 Связь", callback_data="contact"),
    InlineKeyboardButton("💳 Оплата", callback_data="payment"),
    InlineKeyboardButton("🛠 Услуги", callback_data="services")
)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    intro_text = (
        "🎬Стань Ближе: яркие эмоции, теплое общение и музыка, объединяющая сердца!\n\n"
        "Мечтаете о крепкой связи со своим ребенком, а он сидит в гаджетах? Хотите создать что-то особенное, что останется с вами на всю жизнь?\n\n"
        "Представьте: вы и ваш ребенок в профессиональной звукозаписывающей студии, вместе создаете песню и снимаете клип! Это не просто развлечение, это уникальный опыт, который укрепит вашу связь и подарит море позитивных эмоций.\n\n"
        "Проект \"Стань Ближе\" идеально подходит для:\n"
        "• Родителей и детей-подростков: Запишите совместную песню и создайте уникальный семейный шедевр.\n"
        "• Супружеских пар: Подарите песню, отражающую вашу любовь и историю.\n"
        "• Корпоративных поздравлений: Песня от коллектива — яркий подарок для партнёров и клиентов.\n\n"
        "Наши преимущества:\n"
        "• ❤️ Тёплые эмоции в уютной атмосфере\n"
        "• 🎧 Проф. оборудование и звук\n"
        "• 🎉 Удобное время по выходным\n"
        "• 🎬 Настоящий клип на память\n\n"
        "Проект \"Стань Ближе\" предлагает:\n"
        "• 1 час студии\n"
        "• Запись песни\n"
        "• Короткий клип\n\n"
        "💰 Стоимость: 12 000 ₽\n\n"
        "Готовы создать незабываемые воспоминания?\n\n"
        "Нажмите кнопку ниже, чтобы начать:"
    )
    try:
        with open("intro.mp4", "rb") as video:
            await bot.send_video(message.chat.id, video, caption=intro_text, reply_markup=main_kb)
    except FileNotFoundError:
        await message.answer("⚠️ Видео intro.mp4 не найдено. Убедитесь, что файл находится рядом с main.py.", reply_markup=main_kb)

@dp.callback_query_handler(lambda c: c.data == 'book_time')
async def process_booking(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Забронирование скоро будет доступно!")

@dp.callback_query_handler(lambda c: c.data == 'contact')
async def process_contact(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "📞 Свяжитесь с нами:\n+7 (963) 200-45-36\nTelegram: @merecords29")

@dp.callback_query_handler(lambda c: c.data == 'payment')
async def process_payment(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "💳 Стоимость услуги: 12 000₽\n\n🔹 QR-код оплаты – скоро появится\n🔹 Счёт ИП – скоро появится")

@dp.callback_query_handler(lambda c: c.data == 'services')
async def process_services(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    kb = InlineKeyboardMarkup(row_width=1)
    for key in SERVICES.keys():
        kb.add(InlineKeyboardButton(key, callback_data=f'service_{key}'))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main"))
    await bot.send_message(callback_query.from_user.id, "Выберите услугу:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith('service_'))
async def process_service_detail(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    key = callback_query.data[len('service_'):]
    info = SERVICES.get(key, "Информация не найдена")
    kb = InlineKeyboardMarkup(row_width=2)
    if key in ["ЗАПИСЬ АУДИОСКАЗКИ", "ЗАПИСЬ ВОКАЛА", "ЗАПИСЬ ПОДКАСТА"]:
        kb.add(InlineKeyboardButton("Забронировать время", callback_data="book_time"))
    kb.add(
        InlineKeyboardButton("Связь", callback_data="contact"),
        InlineKeyboardButton("Оплата", callback_data="payment"),
        InlineKeyboardButton("⬅️ Назад к услугам", callback_data="services")
    )
    await bot.send_message(callback_query.from_user.id, info, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == 'back_to_main')
async def back_to_main(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Вы вернулись в главное меню.", reply_markup=main_kb)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
