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
    photo = State()
    phone = State()


# =========================
# START
# =========================
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):

    await state.set_state(Form.name)

    await message.answer("Введите ФИО")


# =========================
# NAME
# =========================
@dp.message(Form.name)
async def get_name(message: Message, state: FSMContext):

    await state.update_data(name=message.text)
    await state.set_state(Form.photo)

    await message.answer("Теперь отправьте фото или скриншот чека.")


# =========================
# PHOTO
# =========================
@dp.message(Form.photo, F.photo)
async def get_photo(message: Message, state: FSMContext):

    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(Form.phone)

    await message.answer("Теперь отправьте номер телефона.")


# =========================
# PHONE + SEND TO MANAGERS
# =========================
@dp.message(Form.phone)
async def get_phone(message: Message, state: FSMContext):

    data = await state.get_data()

    name = data["name"]
    photo = data["photo"]
    phone = message.text

    username = message.from_user.username
    username_text = f"@{username}" if username else "не указан"

    caption = (
        f"НОВАЯ ЗАЯВКА\n\n"
        f"ФИО: {name}\n"
        f"Телефон: {phone}\n"
        f"Username: {username_text}\n"
        f"ID: {message.from_user.id}"
    )

    for manager in MANAGERS:
        await bot.send_photo(
            chat_id=manager,
            photo=photo,
            caption=caption
        )

    await message.answer(
        "✅ Спасибо! Мы получили данные и отправили на проверку."
    )

    await state.clear()


# =========================
# MAIN
# =========================
async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())