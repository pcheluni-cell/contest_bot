from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
import asyncio

# ТОКЕН БОТА
TOKEN = "8072709295:AAGhzMAhfZFbkYqlFT3cYC4IEJhW1eku9Xs"

# ID МЕНЕДЖЕРОВ
MANAGERS = [
    111111111,
    222222222,
    333333333
]

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# Временное хранение данных пользователей
users_data = {}


# СТАРТ
@dp.message(CommandStart())
async def start(message: Message):

    users_data[message.from_user.id] = {}

    await message.answer(
        "Введите ФИО"
    )


# ОБРАБОТКА ТЕКСТА
@dp.message(F.text)
async def text_handler(message: Message):

    user_id = message.from_user.id

    # =========================
    # ОТВЕТЫ МЕНЕДЖЕРОВ
    # =========================
    if user_id in MANAGERS:

        if message.reply_to_message:

            reply_text = (
                message.reply_to_message.text
                or message.reply_to_message.caption
            )

            if reply_text and "ID:" in reply_text:

                try:

                    target_id = int(
                        reply_text.split("ID:")[1]
                        .split("\n")[0]
                        .strip()
                    )

                    # ОТПРАВКА ПОЛЬЗОВАТЕЛЮ
                    await bot.send_message(
                        target_id,
                        f"Сообщение от менеджера:\n\n{message.text}"
                    )

                    # УВЕДОМЛЕНИЕ ДРУГИМ МЕНЕДЖЕРАМ
                    for manager in MANAGERS:

                        if manager != user_id:

                            await bot.send_message(
                                manager,
                                f"Менеджер ответил пользователю {target_id}:\n\n{message.text}"
                            )

                    await message.answer(
                        "Сообщение отправлено пользователю"
                    )

                except Exception as e:
                    print(e)

        return

    # =========================
    # ПОЛЬЗОВАТЕЛИ
    # =========================

    if user_id not in users_data:
        return

    # ФИО
    if "name" not in users_data[user_id]:

        users_data[user_id]["name"] = message.text

        await message.answer(
            "Пришлите фото чека"
        )

        return

    # ТЕЛЕФОН
    if "phone" not in users_data[user_id]:

        users_data[user_id]["phone"] = message.text

        data = users_data[user_id]

        username = message.from_user.username

        if username:
            username_text = f"@{username}"
        else:
            username_text = "не указан"

        caption = (
            f"НОВАЯ ЗАЯВКА\n\n"
            f"ФИО: {data['name']}\n"
            f"Телефон: {data['phone']}\n"
            f"Username: {username_text}\n"
            f"ID: {user_id}"
        )

        # ОТПРАВКА ВСЕМ МЕНЕДЖЕРАМ
        for manager in MANAGERS:

            await bot.send_photo(
                chat_id=manager,
                photo=data["photo"],
                caption=caption
            )

        await message.answer(
            "Ожидайте, менеджер проверяет ваш заказ и ответит вам."
        )

        del users_data[user_id]

        return


# ОБРАБОТКА ФОТО
@dp.message(F.photo)
async def photo_handler(message: Message):

    user_id = message.from_user.id

    if user_id not in users_data:

        await message.answer(
            "Нажмите /start"
        )

        return

    # ЕСЛИ ФИО ЕЩЁ НЕ ВВЕДЕНО
    if "name" not in users_data[user_id]:

        await message.answer(
            "Сначала введите ФИО"
        )

        return

    # СОХРАНЯЕМ ФОТО
    users_data[user_id]["photo"] = message.photo[-1].file_id

    await message.answer(
        "Введите номер телефона"
    )


# ЗАПУСК БОТА
async def main():

    print("BOT STARTED")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())