from aiogram import Router, F
from aiogram.types import Message
from .keybroads import profile_keyboard

router = Router()

@router.message(F.text == "📋 Личные данные")
async def show_personal_data(message: Message):
    await message.answer("Здесь будут ваши личные данные", reply_markup=profile_keyboard)

@router.message(F.text == "📜 История нарушений")
async def show_violation_history(message: Message):
    await message.answer("Здесь будет история ваших нарушений", reply_markup=profile_keyboard)

@router.message(F.text == "🔙 Назад")
async def back_to_main(message: Message):
    from .keybroads import main_keyboard
    await message.answer("Возвращаемся в главное меню", reply_markup=main_keyboard)