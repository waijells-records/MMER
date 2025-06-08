import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import requests
import uuid

BOT_TOKEN = "ВАШ_ТОКЕН_БОТА"
YOOKASSA_SHOP_ID = "ВАШ_SHOP_ID"
YOOKASSA_SECRET_KEY = "ВАШ_SECRET_KEY"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Главное меню
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🎬 Стань Ближе", callback_data="intro"),
        InlineKeyboardButton("💳 Оплатить", callback_data="pay"),
        InlineKeyboardButton("📞 Связаться", url="https://t.me/merecords29")
    )
    return keyboard

# Обработка команды /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Добро пожаловать в проект «Стань Ближе»!\n\n"
        "Я помогу вам записать песню и клип с близкими в студии ❤️",
        reply_markup=main_menu()
    )

# Встроенное интро + видео
@dp.callback_query_handler(lambda c: c.data == "intro")
async def show_intro(callback_query: types.CallbackQuery):
    await bot.send_video(callback_query.from_user.id, open("интро.mp4", "rb"))
    await bot.send_message(callback_query.from_user.id,
        "🎬 *Стань Ближе*: яркие эмоции, теплое общение и музыка, объединяющая сердца!\n\n"
        "Представьте: вы и ваш ребёнок в студии — записываете песню и клип. Это не просто развлечение, это память на всю жизнь.",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# Генерация платёжной ссылки
def create_payment_link(amount=12000):
    payment_id = str(uuid.uuid4())
    headers = {
        "Authorization": f"Basic {YOOKASSA_SHOP_ID}:{YOOKASSA_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "amount": {
            "value": f"{amount}.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/merecords29"
        },
        "description": "Оплата за участие в проекте «Стань Ближе»",
        "capture": True,
        "metadata": {"order_id": payment_id}
    }
    response = requests.post(
        "https://api.yookassa.ru/v3/payments",
        json=data,
        auth=(YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY)
    )
    result = response.json()
    return result.get("confirmation", {}).get("confirmation_url", "Ошибка при создании оплаты")

# Оплата
@dp.callback_query_handler(lambda c: c.data == "pay")
async def handle_payment(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    payment_url = create_payment_link()
    await bot.send_message(callback_query.from_user.id, 
        f"Для оплаты нажмите на кнопку ниже или отсканируйте QR-код на странице оплаты:\n\n[Перейти к оплате]({payment_url})",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
