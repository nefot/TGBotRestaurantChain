# SecurityStaff/telegramBot/handlers/security_handlers.py

from aiogram import types
from aiogram.filters import CommandStart
from aiogram.types import Message
from SecurityStaff.models import Violation
from ..keyboards import security_keyboard, violations_management_keyboard
from ..templates import violation_template
from asgiref.sync import sync_to_async


# Обработчик команды /start
async def command_start_handler(message: Message) -> None:
    await message.answer("Добро пожаловать в службу безопасности!", reply_markup=security_keyboard)


# Обработчик кнопки "Управление нарушениями"
async def handle_violations_menu(message: Message) -> None:
    await message.answer("Выберите действие:", reply_markup=violations_management_keyboard)


# Обработчик кнопки "Просмотр нарушений"
async def handle_view_violations(message: Message) -> None:
    violations = await sync_to_async(list)(Violation.objects.filter(feedback__user_id=message.from_user.id))
    if violations:
        for violation in violations:
            await message.answer(violation_template(violation))
    else:
        await message.answer("У вас нет нарушений.")


# Обработчик кнопки "Назад"
async def handle_back(message: Message) -> None:
    await message.answer("Возвращаемся в главное меню.", reply_markup=security_keyboard)
