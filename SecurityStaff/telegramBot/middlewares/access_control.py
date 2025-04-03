from typing import Callable, Dict, Any, Awaitable

from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from asgiref.sync import sync_to_async

from SecurityStaff.models import Waiter


class AccessMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: types.TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        message = data.get("event_update").message if data.get("event_update") else None
        if not message:
            return await handler(event, data)

        username = f"@{message.from_user.username}" if message.from_user.username else None
        if not username:
            await message.answer("❌ У вас нет @username в Telegram. Доступ запрещён.")
            return

        # Проверяем, есть ли этот username в базе официантов и активен ли доступ
        waiter = await sync_to_async(lambda: Waiter.objects.filter(user_id=username).first())()

        if not waiter:
            await message.answer("❌ У вас нет доступа к этому боту.")
            return

        if not waiter.has_access:
            await message.answer("🚫 Доступ к боту заблокирован.")
            return

        return await handler(event, data)
