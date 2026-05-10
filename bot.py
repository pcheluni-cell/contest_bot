from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
import asyncio

# ТОКЕН БОТА
TOKEN = "8072709295:AAGhzMAhfZFbkYqlFT3cYC4IEJhW1eku9Xs"

# ID МЕНЕДЖЕРОВ
MANAGERS = [1101671929, 786753371]

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# ХРАНЕНИЕ ДАННЫХ
users_data = {}


# =========================
# START
# =========================
@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    users_data[user_id] = {
        "step": "name"
    }

    await message.answer("Введите ФИО")


# =========================
# ТЕКСТ
# =========================
@dp.message(F.text)
async def text_handler(message: Message):

    user_id = message.from_user.id
    text = message.text

    # =========================
    # МЕНЕДЖЕРЫ
    # =========================
    if user_id in MANAGERS:

        if message.reply_to_message:

            reply_text = message.reply_to_message.text or message.reply_to_message.caption

            if reply_text and "ID:" in reply_text:

                try:
                    target_id = int(
                        reply_text.split("ID:")[1].split("\n")[0].strip()
                    )

                    await bot.send_message(
                        target_id,
                        f"Сообщение от менеджера:\n\n{text}"
                    )

                    for manager in MANAGERS:
                        if manager != user_id:
                            await bot.send_message(
                                manager,
                                f"Ответ менеджера пользователю {target_id}:\n\n{text}"
                            )

                    await message.answer("Сообщение отправлено пользователю")

                except Exception as e:
                    print("Ошибка:", e)

        return

    # =========================
    # ПОЛЬЗОВАТЕЛИ
    # =========================
    if user_id not in users_data:
        await message.answer("Нажмите /start")
        return

    user = users_data[user_id]

    # ---- ФИО ----
    if user["step"] == "name":
        user["name"] = text
        user["step"] = "photo"

        await message.answer("Пришлите фото чека")
        return

    # ---- ТЕЛЕФОН ----
    if user["step"] == "phone":
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

        for manager in MANAGERS:
            await bot.send_photo(
                chat_id=manager,
                photo=user["photo"],
                caption=caption
            )

        await message.answer("Ожидайте, менеджер свяжется с вами.")

        del users_data[user_id]
        return


# =========================
# ФОТО
# =========================
@dp.message(F.photo)
async def photo_handler(message: Message):

    user_id = message.from_user.id

    if user_id not in users_data:
        await message.answer("Нажмите /start")
        return

    user = users_data[user_id]

    if user["step"] != "photo":
        await message.answer("Сначала введите ФИО")
        return

    user["photo"] = message.photo[-1].file_id
    user["step"] = "phone"

    await message.answer("Введите номер телефона")


# =========================
# ЗАПУСК
# =========================
async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())