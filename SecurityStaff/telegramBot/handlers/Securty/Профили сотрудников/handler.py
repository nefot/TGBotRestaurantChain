# Профили сотрудников/handler.py
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery


async def handle(message: Message):
    """Обработчик для reply-версии кнопки"""
    await message.answer("Вы в разделе профилей сотрудников. Вот список...")


async def handle_callback(callback: CallbackQuery):
    """Обработчик для inline-версии кнопки"""
    await callback.message.edit_text("Вы в разделе профилей сотрудников. Выберите действие:")
    await callback.answer()


def register_handlers(router):
    """Дополнительные обработчики для этого раздела"""

    @router.message(Command("employees"))
    async def cmd_employees(message: Message):
        await message.answer("Специальная команда для профилей сотрудников")

