from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_pagination_keyboard(current_page: int, total_pages: int):
    keyboard = []
    if total_pages > 1:
        row = []
        if current_page > 1:
            row.append(KeyboardButton(text="⬅️ Назад"))
        if current_page < total_pages:
            row.append(KeyboardButton(text="Вперед ➡️"))
        keyboard.append(row)
    keyboard.append([KeyboardButton(text="✅ Выбрать")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


from typing import List, Any, Callable


async def show_paginated_list(
        message,
        items: List[Any],
        page: int,
        items_per_page: int,
        format_func: Callable[[Any, int], str],
        state: FSMContext,
        state_key: str
):
    total_pages = (len(items) + items_per_page - 1) // items_per_page
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_items = items[start_idx:end_idx]

    # Формируем текст сообщения
    message_text = "\n".join(
        [format_func(item, start_idx + i + 1) for i, item in enumerate(page_items)]
    )

    # Сохраняем текущее состояние
    await state.update_data({
        state_key: {
            "items"      : items,
            "page"       : page,
            "total_pages": total_pages,
            "selected"   : None
        }
    })

    # Отправляем сообщение с клавиатурой
    await message.answer(
        message_text,
        reply_markup=get_pagination_keyboard(page, total_pages)
    )
