# SecurityStaff/telegramBot/SecurityBot.py

import asyncio
import os
import django
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from .bot_config import SECURITY_BOT_TOKEN
from .handlers.security_handlers import (command_start_handler, handle_violations_menu, handle_view_violations,
                                         handle_back)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src_tgbotrestaurantchain.settings')
django.setup()

bot = Bot(token=SECURITY_BOT_TOKEN)
dp = Dispatcher()

# Регистрация обработчиков
dp.message.register(command_start_handler, CommandStart())
dp.message.register(handle_violations_menu, lambda message: message.text == "📋 Управление нарушениями")
dp.message.register(handle_view_violations, lambda message: message.text == "🔍 Просмотр нарушений")
dp.message.register(handle_back, lambda message: message.text == "🔙 Назад")  # Регистрация обработчика для кнопки
# "Назад"


# Запуск бота
async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
