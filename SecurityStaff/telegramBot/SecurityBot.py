import os
import asyncio
import django
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp_socks import ProxyConnector

# Сначала настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src_tgbotrestaurantchain.settings')
django.setup()

# Затем импортируем остальные компоненты
from SecurityStaff.telegramBot.middlewares.access_control import AccessMiddleware
from SecurityStaff.telegramBot.bot_config import SECURITY_BOT_TOKEN
from SecurityStaff.telegramBot.handlers import security_handlers


async def main():
    # Настройка прокси (если нужно)
    proxy = "socks5://127.0.0.1:1080"  # или ваш реальный прокси
    connector = ProxyConnector.from_url(proxy) if proxy else None

    storage = MemoryStorage()
    bot = Bot(token="941769226:AAGLfZzmKyA-jsj2C6aNHY8A0l-N_mGhpl4", connector=connector)
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