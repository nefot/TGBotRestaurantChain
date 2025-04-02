from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async

from SecurityStaff.models import Waiter
from ..keyboards import profile_management_keyboard, security_keyboard, back_keyboard
from .employee_profiles import show_waiter_profile

router = Router()


@router.message(F.text == "👤 Управление профилем")
async def handle_profile_management(message: Message):
    """Обработчик кнопки управления профилем"""
    await message.answer(
        "Выберите действие с профилями:",
        reply_markup=profile_management_keyboard
    )


# profile_management.py
@router.message(F.text == "🆔 Мой профиль")
async def handle_my_profile(message: Message, bot):
    """Обработчик кнопки 'Мой профиль'"""
    if not message.from_user.username:
        await message.answer("У вас не установлен username в Telegram")
        return

    user_id = f"@{message.from_user.username}"

    try:
        waiter = await sync_to_async(Waiter.objects.get)(user_id=user_id)
        await show_waiter_profile(message, waiter, bot)
    except Waiter.DoesNotExist:
        await message.answer(
            "Ваш профиль не найден в системе. Обратитесь к администратору.",
            reply_markup=back_keyboard
        )


@router.message(F.text == "🔙 Назад")
async def handle_back_from_profile_management(message: Message, state: FSMContext):
    """Обработчик кнопки 'Назад' в меню управления профилями"""
    await state.clear()
    await message.answer(
        "Главное меню:",
        reply_markup=security_keyboard
    )
