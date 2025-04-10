import asyncio
import os

import django
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp_socks import ProxyConnector
from dotenv import load_dotenv

from SecurityStaff.telegramBot.handlers.Waiter.access_control import AccessMiddleware

load_dotenv()
# Сначала настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src_tgbotrestaurantchain.settings')
django.setup()

from SecurityStaff.telegramBot.handlers.Waiter.waiter_handlers import router

async def main():
    # Настройка прокси (если нужно)
    connector = ProxyConnector.from_url("socks5://127.0.0.1:1080", rdns=True)

    storage = MemoryStorage()
    bot = Bot(token=os.getenv("WAITER_BOT_TOKEN"))
    dp = Dispatcher(storage=storage)
    dp.message.middleware(AccessMiddleware())


    dp.include_router(router)  # Используем router напрямую

    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())