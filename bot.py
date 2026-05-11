from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
import asyncio

# =========================
# TOKEN
# =========================
TOKEN = "8072709295:AAEowfFbPHBSgyFGLWY0KMCqv26hme0CmeE"

# =========================
# MANAGERS
# =========================
MANAGERS = [
    1101671929,
    786753371,
    1277262647
]

# =========================
# BOT
# =========================
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# =========================
# DATA
# =========================
users_data = {}

# message_id менеджера -> user_id
message_map = {}


# =========================
# START
# =========================
@dp.message(CommandStart())
async def start(message: Message):

    users_data[message.from_user.id] = {
        "step": "name"
    }

    await message.answer(
        "Введите ФИО"
    )


# =========================
# TEXT
# =========================
@dp.message(F.text)
async def text_handler(message: Message):

    user_id = message.from_user.id
    text = message.text

    # =========================
    # MANAGERS
    # =========================
    if user_id in MANAGERS:

        if message.reply_to_message:

            reply_id = message.reply_to_message.message_id

            if reply_id in message_map:

                target_user_id = message_map[reply_id]

                try:

                    # сообщение пользователю
                    await bot.send_message(
                        target_user_id,
                        f"Сообщение от менеджера:\n\n{text}"
                    )

                    # другим менеджерам
                    for manager in MANAGERS:

                        if manager != user_id:

                            await bot.send_message(
                                manager,
                                f"📩 Менеджер ответил пользователю {target_user_id}\n\n"
                                f"От: {message.from_user.full_name}\n\n"
                                f"{text}"
                            )

                    await message.answer(
                        "Сообщение отправлено пользователю"
                    )

                except Exception as e:

                    await message.answer(
                        f"Ошибка: {e}"
                    )

        return

    # =========================
    # USERS
    # =========================
    if user_id not in users_data:

        users_data[user_id] = {
            "step": "name"
        }

    user = users_data[user_id]

    # =========================
    # STEP NAME
    # =========================
    if user.get("step") == "name":

    	print("STEP NAME WORKS")

    	user["name"] = text
    	user["step"] = "photo"

    	print(users_data)

    	await message.answer(
        	"Спасибо! Теперь отправьте фото или скриншот чека."
    	)

    return

    # =========================
    # STEP PHONE
    # =========================
    if user["step"] == "phone":

        user["phone"] = text

        username = message.from_user.username

        if username:
            username_text = f"@{username}"
        else:
            username_text = "не указан"

        caption = (
            f"НОВАЯ ЗАЯВКА\n\n"
            f"ФИО: {user['name']}\n"
            f"Телефон: {user['phone']}\n"
            f"Username: {username_text}\n"
            f"ID: {user_id}"
        )

        # отправка менеджерам
        for manager in MANAGERS:

            try:

                msg = await bot.send_photo(
                    chat_id=manager,
                    photo=user["photo"],
                    caption=caption
                )

                message_map[msg.message_id] = user_id

            except Exception as e:

                print("SEND ERROR:", e)

        await message.answer(
            "✅ Спасибо! Мы получили ваши данные и отправили их на проверку.\n\n"
            "После подтверждения мы отправим ваш номер участника 🎟️"
        )

        del users_data[user_id]

        return


# =========================
# PHOTO
# =========================
@dp.message(F.photo)
async def photo_handler(message: Message):
    print("PHOTO RECEIVED")
    user_id = message.from_user.id

    if user_id not in users_data:

        await message.answer(
            "Нажмите /start"
        )

        return

    user = users_data[user_id]

    # ждём фото только после ФИО
    if user["step"] != "photo":

        await message.answer(
            "Сначала введите ФИО"
        )

        return

    user["photo"] = message.photo[-1].file_id
    user["step"] = "phone"

    await message.answer(
        "Теперь отправьте номер телефона."
    )


# =========================
# MAIN
# =========================
async def main():

    print("BOT STARTED")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())