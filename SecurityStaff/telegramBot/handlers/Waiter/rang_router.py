from aiogram import Router, F
from aiogram.types import Message

from .keybroads import main_keyboard

router = Router()


@router.message(F.text == "⭐ Рейтинговая система")
async def show_rating(message: Message):
    await message.answer("Текущий рейтинг сотрудников...", reply_markup=main_keyboard)
