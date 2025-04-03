import asyncio
import os
import django
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from SecurityStaff.telegramBot.middlewares.access_control import AccessMiddleware
from .bot_config import SECURITY_BOT_TOKEN
from .handlers import security_handlers
from aiogram import Bot
from aiohttp_socks import ProxyConnector

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src_tgbotrestaurantchain.settings')
django.setup()


proxy = "socks5://127.0.0.1:1080"
connector = ProxyConnector.from_url(proxy)



async def main():
    storage = MemoryStorage()
    bot = Bot(token=SECURITY_BOT_TOKEN, connector=connector)
    dp = Dispatcher(storage=storage)
    dp.message.middleware(AccessMiddleware())

    dp.include_router(security_handlers.router)

    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())