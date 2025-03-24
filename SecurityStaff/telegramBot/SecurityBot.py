import asyncio
import os
import django
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from .bot_config import SECURITY_BOT_TOKEN
from .handlers import security_handlers

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src_tgbotrestaurantchain.settings')
django.setup()


async def main():
    storage = MemoryStorage()
    bot = Bot(token=SECURITY_BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    dp.include_router(security_handlers.router)

    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())