from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
import asyncio

TOKEN = "8654850512:AAE8OVmpzhOXlU02DOxFxdi9C2BwGb5PPu4"

# ID менеджера
MANAGER_ID = 1101671929

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

users_data = {}


# Команда START
@dp.message(CommandStart())
async def start(message: Message):

    users_data[message.from_user.id] = {}

    await message.answer(
        "Введите ФИО"
    )


# Получение текста
@dp.message(F.text)
async def get_text(message: Message):

    user_id = message.from_user.id

    if user_id not in users_data:
        return

    # ФИО
    if "name" not in users_data[user_id]:

        users_data[user_id]["name"] = message.text

        await message.answer(
            "Введите номер телефона"
        )

        return

    # Телефон
    if "phone" not in users_data[user_id]:

        users_data[user_id]["phone"] = message.text

        await message.answer(
            "Пришлите фото чека"
        )

        return


# Получение фото
@dp.message(F.photo)
async def get_photo(message: Message):

    user_id = message.from_user.id

    if user_id not in users_data:
        await message.answer("Нажмите /start")
        return

    data = users_data[user_id]

    if "name" not in data or "phone" not in data:
        await message.answer("Сначала заполните данные")
        return

    username = message.from_user.username

    if username:
        username_text = f"@{username}"
    else:
        username_text = "Не указан"

    caption = (
        f"Новая заявка\n\n"
        f"ФИО: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Username: {username_text}\n"
        f"ID пользователя: {user_id}"
    )

    try:

        # Отправка фото менеджеру
        await bot.send_photo(
            chat_id=MANAGER_ID,
            photo=message.photo[-1].file_id,
            caption=caption
        )

        # Сообщение пользователю
        await message.answer(
            "Ожидайте, менеджер проверяет ваш заказ и ответит вам."
        )

        # Очистка данных
        del users_data[user_id]

    except Exception as e:

        print(e)

        await message.answer(
            "Ошибка отправки заявки."
        )


# Запуск бота
async def main():

    print("Бот запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())