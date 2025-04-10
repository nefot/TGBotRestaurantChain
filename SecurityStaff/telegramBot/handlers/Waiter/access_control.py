from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import ReplyKeyboardRemove
from asgiref.sync import sync_to_async
from SecurityStaff.models import Waiter


class AccessMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if not (message := data.get('event_update', {}).message):
            return await handler(event, data)

        if not message.from_user.username:
            await message.answer("❌ У вас нет @username в Telegram")
            return

        user_id = f"@{message.from_user.username.lower()}"

        try:
            waiter = await sync_to_async(Waiter.objects.get)(user_id__iexact=user_id)
            data['waiter'] = waiter  # Добавляем официанта в data
        except Waiter.DoesNotExist:
            await message.answer(
                "❌ Ваш профиль не найден в системе. Обратитесь к администратору.",
                reply_markup=ReplyKeyboardRemove()
            )
            return

        return await handler(event, data)