import asyncio
from django.core.management.base import BaseCommand
from SecurityStaff.telegramBot.SecurityBot import main as security_main
from SecurityStaff.telegramBot.WaiterBot import main as waiter_main
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()


class Command(BaseCommand):
    help = "Запускает Telegram-ботов для службы безопасности и официантов."

    def handle(self, *args, **options):
        async def run_bots():
            await asyncio.gather(
                security_main(),
                waiter_main()
            )

        asyncio.run(run_bots())
