import os
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db.models import Prefetch

from SecurityStaff.models import Violation, ViolationWaiter
from .service import prepare_violation_message
from ..keyboards import back_to_menu_keyboard, violations_management_keyboard

router = Router()
VIOLATIONS_PER_PAGE = 5


async def get_violations_with_waiters(page: int):
    """Асинхронно получает нарушения с пред загрузкой связанных данных"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    return await sync_to_async(list)(
        Violation.objects.filter(
            date__range=[start_date, end_date]
        ).select_related('violation_type', 'status')
        .prefetch_related(
            Prefetch('violation_waiters',
                     queryset=ViolationWaiter.objects.select_related('waiter'))
        )
        .order_by('-date', 'waiters__last_name')
        [page * VIOLATIONS_PER_PAGE:(page + 1) * VIOLATIONS_PER_PAGE]
    )


async def get_media_path(image_field):
    """Получает полный путь к файлу в медиа"""
    if not image_field:
        return None
    return os.path.join(settings.MEDIA_ROOT, image_field.name)


@router.message(F.text == "🔙 Назад")
async def handle_back_button(message: Message, state: FSMContext):
    """Обработчик кнопки Назад в обычной клавиатуре"""
    await state.clear()
    await message.answer(
        "Возвращаемся в главное меню",
        reply_markup=violations_management_keyboard
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Назад' в меню нарушений"""
    try:
        await callback.message.delete()

        await state.clear()

        await callback.message.answer(
            "Меню управления нарушениями:",
            reply_markup=violations_management_keyboard
        )
    except Exception as e:
        await callback.answer("Произошла ошибка, попробуйте еще раз")

    await callback.answer()


async def send_violation_details(chat_id: int, violation, bot):
    """Отправляет полную информацию о нарушении с фото"""
    message_data = await prepare_violation_message(violation)
    text = message_data["text"]

    if message_data["error_message"]:
        text = f"{text}\n\n{message_data['error_message']}"

    if message_data["photo"] and not message_data["error_message"]:
        await bot.send_photo(
            chat_id=chat_id,
            photo=message_data["photo"],
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=back_to_menu_keyboard
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=back_to_menu_keyboard
        )


@router.message(F.text == "🔍 Просмотр нарушений")
async def show_violations_menu(message: Message, state: FSMContext, bot):
    await state.update_data(current_page=0)
    await display_violations(message, state, bot)


async def display_violations(message: Message, state: FSMContext, bot):
    data = await state.get_data()
    current_page = data.get('current_page', 0)

    violations = await get_violations_with_waiters(current_page)

    if not violations:
        await message.answer("Нарушений за последнюю неделю не найдено.",
                             reply_markup=back_to_menu_keyboard)
        return

    builder = InlineKeyboardBuilder()
    for violation in violations:
        waiter = await sync_to_async(lambda: violation.violation_waiters.first().waiter)()
        builder.button(
            text=f"{violation.date.strftime('%d.%m')} {waiter.last_name} {violation.violation_type.name}",
            callback_data=f"violation_{violation.id}"
        )
    builder.adjust(1)

    pagination_buttons = []
    if current_page > 0:
        pagination_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="prev_page"
        ))

    next_page_violations = await get_violations_with_waiters(current_page + 1)
    if next_page_violations:
        pagination_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data="next_page"
        ))

    if pagination_buttons:
        builder.row(*pagination_buttons)

    builder.row(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="prev_page"
    ))

    await message.answer(
        "Последние нарушения (неделя):",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.startswith("violation_"))
async def show_violation_details(callback: CallbackQuery, bot):
    violation_id = int(callback.data.split("_")[1])
    violation = await sync_to_async(
        lambda: Violation.objects.select_related('violation_type', 'status')
        .prefetch_related(
            Prefetch('violation_waiters',
                     queryset=ViolationWaiter.objects.select_related('waiter'))
        )
        .get(id=violation_id)
    )()

    await send_violation_details(callback.from_user.id, violation, bot)
    await callback.answer()


@router.callback_query(F.data.in_(["prev_page", "next_page"]))
async def handle_pagination(callback: CallbackQuery, state: FSMContext, bot):
    data = await state.get_data()
    current_page = data.get('current_page', 0)

    if callback.data == "prev_page" and current_page > 0:
        current_page -= 1
    elif callback.data == "next_page":
        current_page += 1

    await state.update_data(current_page=current_page)
    await callback.message.delete()
    await display_violations(callback.message, state, bot)
    await callback.answer()


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "Меню управления нарушениями:",
        reply_markup=violations_management_keyboard
    )
    await callback.answer()


@router.message(lambda message: message.text.isdigit())
async def show_violation_by_id(message: Message, bot):
    try:
        violation = await sync_to_async(
            lambda: Violation.objects.select_related('violation_type', 'status')
            .prefetch_related(
                Prefetch('violation_waiters',
                         queryset=ViolationWaiter.objects.select_related('waiter'))
            )
            .get(id=int(message.text))
        )()

        await send_violation_details(message.chat.id, violation, bot)
    except Violation.DoesNotExist:
        await message.answer("Нарушение с таким ID не найдено.",
                             reply_markup=back_to_menu_keyboard)
