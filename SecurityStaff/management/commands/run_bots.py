import asyncio
import logging
from django.core.management.base import BaseCommand
from SecurityStaff.telegramBot.SecurityBot import main as security_main
from SecurityStaff.telegramBot.WaiterBot import main as waiter_main

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Запускает Telegram-ботов для службы безопасности и официантов."

    def handle(self, *args, **options):
        # Настройка логирования
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        logger.info("🟢 Начало запуска ботов...")

        async def run_bots():
            try:
                logger.info("Попытка запуска SecurityBot...")
                security_task = asyncio.create_task(security_main())

                logger.info("Попытка запуска WaiterBot...")
                waiter_task = asyncio.create_task(waiter_main())

                await asyncio.gather(security_task, waiter_task)

            except Exception as e:
                logger.error(f"❌ Ошибка при запуске ботов: {e}", exc_info=True)
                # Закрываем все задачи при ошибке
                for task in asyncio.all_tasks():
                    task.cancel()
                raise

        try:
            asyncio.run(run_bots())
            logger.info("🟢 Оба бота успешно запущены и работают")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
            self.stderr.write(f"Ошибка: {e}")