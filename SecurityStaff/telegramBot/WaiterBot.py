

import asyncio
import os
import django
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from .bot_config import WAITER_BOT_TOKEN
from .handlers.waiter_handlers import command_start_handler, handle_violation_history, handle_rating, handle_profile


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src_tgbotrestaurantchain.settings')
django.setup()

bot = Bot(token=WAITER_BOT_TOKEN)
dp = Dispatcher()


dp.message.register(command_start_handler, CommandStart())
dp.message.register(handle_violation_history, lambda message: message.text == "📖 История нарушений")
dp.message.register(handle_rating, lambda message: message.text == "📊 Рейтинг")
dp.message.register(handle_profile, lambda message: message.text == "👤 Мой профиль")



async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
