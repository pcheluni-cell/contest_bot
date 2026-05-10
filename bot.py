from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
import asyncio

TOKEN = "8072709295:AAGhzMAhfZFbkYqlFT3cYC4IEJhW1eku9Xs"

MANAGERS = [1101671929, 786753371]

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

users_data = {}


# =========================
# START
# =========================
@dp.message(CommandStart())
async def start(message: Message):

    users_data[message.from_user.id] = {}

    await message.answer("Введите ФИО")


# =========================
# TEXT
# =========================
@dp.message(F.text)
async def text_handler(message: Message):

    user_id = message.from_user.id
    text = message.text

    if user_id in MANAGERS:
        return

    if user_id not in users_data:
        users_data[user_id] = {}

    user = users_data[user_id]

    # ФИО
    if "name" not in user:
        user["name"] = text
        await message.answer("Отправьте фото чека")
        return

    # ТЕЛЕФОН (финальный шаг)
    if "photo" in user:

        user["phone"] = text

        username = message.from_user.username
        username_text = f"@{username}" if username else "не указан"

        caption = (
            f"НОВАЯ ЗАЯВКА\n\n"
            f"ФИО: {user['name']}\n"
            f"Телефон: {user['phone']}\n"
            f"Username: {username_text}\n"
            f"ID: {user_id}"
        )

        # ОТПРАВКА МЕНЕДЖЕРАМ
        for manager in MANAGERS:
            await bot.send_photo(
                chat_id=manager,
                photo=user["photo"],
                caption=caption
            )

        # ОТВЕТ ПОЛЬЗОВАТЕЛЮ (ВАЖНОЕ ИСПРАВЛЕНИЕ)
        await message.answer("Ожидайте, менеджер проверяет номер заказа")

        # очистка
        users_data.pop(user_id, None)
        return

    await message.answer("Сначала отправьте фото")


# =========================
# PHOTO
# =========================
@dp.message(F.photo)
async def photo_handler(message: Message):

    user_id = message.from_user.id

    if user_id not in users_data:
        users_data[user_id] = {}

    users_data[user_id]["photo"] = message.photo[-1].file_id

    await message.answer("Введите номер телефона")


# =========================
# START BOT
# =========================
async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())