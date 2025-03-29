# SecurityBot.py
from aiogram import Bot, Dispatcher
import os

from aiogram.types import Message

from SecurityStaff.management.commands.fill_test_data import Command
from SecurityStaff.telegramBot.handlers.Securty.core.keyboard_generator import KeyboardHandlerGenerator


class SecurityBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.keyboard_handler = KeyboardHandlerGenerator(
            base_path=os.path.join(os.path.dirname(__file__), "handlers/Securty"),
            router=self.dp
        )

    async def start(self):
        # Загружаем все обработчики
        self.handlers = await self.keyboard_handler.load_handlers()

        # Регистрируем главное меню
        @self.dp.message(Command("start"))
        async def cmd_start(message: Message):
            keyboard = await self.keyboard_handler.generate_keyboard("root")
            await message.answer("Главное меню:", reply_markup=keyboard)

        # Запускаем бота
        await self.dp.start_polling(self.bot)