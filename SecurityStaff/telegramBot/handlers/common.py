from aiogram import types
from aiogram.dispatcher import Dispatcher

def register_handlers(dp: Dispatcher):
    @dp.message_handler(commands=['help'])
    async def help(message: types.Message):
        await message.answer("Это общий обработчик помощи.")