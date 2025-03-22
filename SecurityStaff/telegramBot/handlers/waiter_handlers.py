# SecurityStaff/telegramBot/handlers/waiter_handlers.py

from aiogram import types
from aiogram.filters import CommandStart
from aiogram.types import Message
from ..keyboards import waiter_keyboard


# Обработчик команды /start
async def command_start_handler(message: Message) -> None:
    await message.answer("Добро пожаловать, сотрудник!", reply_markup=waiter_keyboard)


# Обработчик кнопки "История нарушений"
async def handle_violation_history(message: Message) -> None:
    await message.answer("Ваша история нарушений будет отображена здесь.")


# Обработчик кнопки "Рейтинг"
async def handle_rating(message: Message) -> None:
    await message.answer("Текущий рейтинг сотрудников будет отображен здесь.")


# Обработчик кнопки "Мой профиль"
async def handle_profile(message: Message) -> None:
    await message.answer("Информация о вашем профиле будет отображена здесь.")
