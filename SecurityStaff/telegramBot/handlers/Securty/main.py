import asyncio
from aiogram import Bot, Dispatcher, executor
from aiogram.fsm.context import FSMContext



API_TOKEN = 'YOUR_BOT_TOKEN'



async def on_startup(dp: Dispatcher):
    await HandlerRegistrar(dp).register_handlers()

    # Регистрируем обработчик для корневого меню
    @dp.callback_query_handler(lambda c: c.data == ".", state="*")
    async def root_menu(callback: types.CallbackQuery, state: FSMContext):
        keyboard = await KeyboardGenerator().generate_keyboard(".")
        await callback.message.edit_text(
            "Главное меню:",
            reply_markup=keyboard
        )
        await callback.answer()


async def on_shutdown(dp: Dispatcher):
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == '__main__':
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot)

    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True
    )