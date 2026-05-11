from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
import asyncio

# =========================
# ТОКЕН
# =========================
TOKEN = "8072709295:AAGhzMAhfZFbkYqlFT3cYC4IEJhW1eku9Xs"

# =========================
# МЕНЕДЖЕРЫ
# =========================
MANAGERS = [1101671929, 786753371,1277262647]

# =========================
# BOT
# =========================
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# =========================
# ДАННЫЕ
# =========================
users_data = {}

# message_id менеджера → user_id
message_map = {}


# =========================
# START
# =========================
@dp.message(CommandStart())
async def start(message: Message):

    users_data[message.from_user.id] = {}

    await message.answer("Введите ФИО")


# =========================
# TEXT HANDLER
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

        	reply_id = message.reply_to_message.message_id

        	if reply_id in message_map:

            		target_user_id = message_map[reply_id]

            		try:
                		await bot.send_message(
                    			target_user_id,
                    			f"Сообщение от менеджера:\n\n{message.text}"
                		)

                		for manager in MANAGERS:

                    			if manager != user_id:

                        			await bot.send_message(
                            				manager,
                            				f"📩 Ответ менеджера пользователю {target_user_id}\n\n"
                            				f"От: {message.from_user.full_name}\n"
                            				f"{message.text}"
                        			)

                		await message.answer("Отправлено пользователю")

            		except Exception as e:
                		await message.answer(f"Ошибка: {e}")

    	return

    # =========================
    # ПОЛЬЗОВАТЕЛИ
    # =========================
    if user_id not in users_data:
        users_data[user_id] = {}

    user = users_data[user_id]

    # ФИО
    if "name" not in user:

        user["name"] = text

        await message.answer("Спасибо! \n Осталось отправить фото или скриншот чека / подтверждения покупки.")

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

        # отправка менеджерам
        for manager in MANAGERS:

            try:
                msg = await bot.send_photo(
                    chat_id=manager,
                    photo=user["photo"],
                    caption=caption
                )

                # связь сообщения
                message_map[msg.message_id] = user_id

            except Exception as e:
                print("SEND ERROR:", e)

        await message.answer("✅ Спасибо! Мы получили ваши данные и отправили их на проверку. \n

Проверка происходит менеджером в порядке очереди в рабочее время с 11:00 до 20:00, поэтому ответ может занять некоторое время. \n

После подтверждения мы отправим ваш номер участника 🎟️")

        del users_data[user_id]

        return


# =========================
# PHOTO HANDLER
# =========================
@dp.message(F.photo)
async def photo_handler(message: Message):

    user_id = message.from_user.id

    if user_id not in users_data:
        users_data[user_id] = {}

    users_data[user_id]["photo"] = message.photo[-1].file_id

    await message.answer("Спасибо! \n Теперь отправьте, пожалуйста, номер телефона для связи.")


# =========================
# START BOT
# =========================
async def main():

    print("BOT STARTED")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())