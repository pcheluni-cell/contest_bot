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
    user_id = message.from_user.id
    users_data[user_id] = {}

    await message.answer("Введите ФИО")


# =========================
# TEXT (ФИО + телефон)
# =========================
@dp.message(F.text)
async def text_handler(message: Message):

    user_id = message.from_user.id
    text = message.text

    # менеджеры не обрабатываются как заявки
    if user_id in MANAGERS:
        return

    if user_id not in users_data:
        users_data[user_id] = {}

    user = users_data[user_id]

    # если ещё нет ФИО → считаем что это ФИО
    if "name" not in user:
        user["name"] = text
        await message.answer("Теперь отправьте фото чека")
        return

    # если есть фото → это телефон и сразу отправляем
    if "photo" in user:

        user["phone"] = text

        username = message.from_user.username
        username_text = f"@{username}" if username else "не указан"

        caption = (
            f"НОВАЯ ЗАЯВКА\n\n"
            f"ФИО: {user.get('name')}\n"
            f"Телефон: {user.get('phone')}\n"
            f"Username: {username_text}\n"
            f"ID: {user_id}"
        )

        for manager in MANAGERS:
            await bot.send_photo(
                chat_id=manager,
                photo=user["photo"],
                caption=caption
            )

        await message.answer("Заявка отправлена менеджеру")

        users_data.pop(user_id, None)
        return


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