from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio

# =========================
# TOKEN
# =========================
TOKEN = "8072709295:AAEowfFbPHBSgyFGLWY0KMCqv26hme0CmeE"

# =========================
# MANAGERS
# =========================
MANAGERS = [1101671929, 786753371, 1277262647]

# =========================
# BOT
# =========================
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=MemoryStorage())

# =========================
# STATES
# =========================
class Form(StatesGroup):
    name = State()
    phone = State()
    order = State()
    photo = State()

# =========================
# MAP (manager_msg_id -> user_id)
# =========================
message_map = {}

# =========================
# START
# =========================
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):

    await message.answer("Введите ФИО")
    await state.set_state(Form.name)


# =========================
# NAME
# =========================
@dp.message(Form.name)
async def get_name(message: Message, state: FSMContext):

    await state.update_data(name=message.text)
    await state.set_state(Form.phone)

    await message.answer(
        "Спасибо!\n\n"
        "Теперь отправьте, пожалуйста, номер телефона для связи."
    )


# =========================
# PHONE
# =========================
@dp.message(Form.phone)
async def get_phone(message: Message, state: FSMContext):

    await state.update_data(phone=message.text)
    await state.set_state(Form.order)

    await message.answer(
        "Отлично 👌\n\n"
        "Теперь отправьте номер вашего заказа."
    )


# =========================
# ORDER
# =========================
@dp.message(Form.order)
async def get_order(message: Message, state: FSMContext):

    await state.update_data(order=message.text)
    await state.set_state(Form.photo)

    await message.answer(
        "Спасибо!\n\n"
        "Осталось отправить фото или скриншот чека / подтверждения покупки."
    )


# =========================
# PHOTO + SEND TO MANAGERS
# =========================
@dp.message(Form.photo, F.photo)
async def get_photo(message: Message, state: FSMContext):

    data = await state.get_data()

    name = data["name"]
    phone = data["phone"]
    order = data["order"]
    photo = message.photo[-1].file_id

    username = message.from_user.username
    username_text = f"@{username}" if username else "не указан"

    caption = (
        f"📌 НОВАЯ ЗАЯВКА\n\n"
        f"ФИО: {name}\n"
        f"Телефон: {phone}\n"
        f"Заказ: {order}\n"
        f"Username: {username_text}\n"
        f"ID: {message.from_user.id}"
    )

    # отправка менеджерам
    for manager in MANAGERS:

        msg = await bot.send_photo(
            chat_id=manager,
            photo=photo,
            caption=caption
        )

        message_map[msg.message_id] = message.from_user.id

    await message.answer(
        "✅ Спасибо! Мы получили ваши данные и отправили их на проверку.\n\n"
        "Проверка происходит менеджером в порядке очереди в рабочее время с 11:00 до 20:00, "
        "поэтому ответ может занять некоторое время.\n\n"
        "После подтверждения мы отправим ваш номер участника 🎟️"
    )

    await state.clear()


# =========================
# MANAGER REPLY SYSTEM
# =========================
@dp.message(F.text)
async def manager_reply(message: Message):

    user_id = message.from_user.id

    if user_id not in MANAGERS:
        return

    if not message.reply_to_message:
        return

    replied_id = message.reply_to_message.message_id

    if replied_id not in message_map:
        return

    target_user_id = message_map[replied_id]

    text = message.text

    # пользователю
    await bot.send_message(
        target_user_id,
        f"📩 Сообщение от менеджера:\n\n{text}"
    )

    # другим менеджерам
    for manager in MANAGERS:

        if manager != user_id:

            await bot.send_message(
                manager,
                f"📢 Ответ менеджера пользователю {target_user_id}\n\n"
                f"От: {message.from_user.full_name}\n\n"
                f"{text}"
            )


# =========================
# MAIN
# =========================
async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())