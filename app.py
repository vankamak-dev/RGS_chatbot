import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


# ===== НАСТРОЙКИ =====
TOKEN = "8664712969:AAEpOC2jKuekC2ZTTjxtCCy0q0fEgUtPJrc"
ADMIN_CHAT_ID = -1003336758908


# ===== BOT =====
bot = Bot(token=TOKEN)
dp = Dispatcher()


# ===== КНОПКИ =====
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📰 Предложить новость")]
    ],
    resize_keyboard=True
)


# ===== СОСТОЯНИЯ =====
class NewsForm(StatesGroup):
    branch = State()
    text = State()
    media = State()


# ===== START =====
@dp.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "Привет! Выбери действие 👇",
        reply_markup=menu
    )


# ===== НАЧАЛО ФОРМЫ =====
@dp.message(F.text == "📰 Предложить новость")
async def start_news(message: Message, state: FSMContext):

    await state.set_state(NewsForm.branch)

    await message.answer(
        "Из какого ты филиала?\n\n"
        "Напиши:\n"
        "• Москва\n"
        "• Питер\n"
        "• Нижний\n"
        "• Сахалин"
    )


# ===== ФИЛИАЛ =====
@dp.message(NewsForm.branch)
async def get_branch(message: Message, state: FSMContext):

    await state.update_data(branch=message.text)

    await state.set_state(NewsForm.text)

    await message.answer(
        "✍️ Теперь напиши саму новость"
    )


# ===== ТЕКСТ =====
@dp.message(NewsForm.text)
async def get_text(message: Message, state: FSMContext):

    await state.update_data(text=message.text)

    await state.set_state(NewsForm.media)

    await message.answer(
        "📸 Теперь отправь фото или видео\n\n"
        "Если медиа нет — напиши: Пропустить"
    )


# ===== МЕДИА =====
@dp.message(NewsForm.media)
async def get_media(message: Message, state: FSMContext):

    data = await state.get_data()

    branch = data["branch"]
    text = data["text"]

    user = message.from_user.full_name

    caption = (
        "📰 НОВАЯ НОВОСТЬ\n\n"
        f"👤 Автор: {user}\n"
        f"📍 Филиал: {branch}\n\n"
        f"📝 Текст:\n{text}"
    )

    # ===== ФОТО =====
    if message.photo:

        photo_id = message.photo[-1].file_id

        await bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=photo_id,
            caption=caption
        )

    # ===== ВИДЕО =====
    elif message.video:

        video_id = message.video.file_id

        await bot.send_video(
            chat_id=ADMIN_CHAT_ID,
            video=video_id,
            caption=caption
        )

    # ===== БЕЗ МЕДИА =====
    elif message.text and message.text.lower() == "пропустить":

        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=caption
        )

    # ===== ОШИБКА =====
    else:

        await message.answer(
            "❌ Отправь фото, видео или напиши 'Пропустить'"
        )

        return

    await state.clear()

    await message.answer(
        "✅ Новость отправлена",
        reply_markup=menu
    )


# ===== MAIN =====
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())