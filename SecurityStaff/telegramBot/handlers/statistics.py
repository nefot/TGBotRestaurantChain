from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from asgiref.sync import sync_to_async

from SecurityStaff.models import Waiter
from .employee_profiles import show_waiter_profile
from .service import (process_selected_employee_number, get_current_month_violations_count,
                      get_total_violations_count, get_formatted_employee_list)
from ..keyboards import (security_keyboard, statistics_keyboard, back_keyboard)

router = Router()


class StatisticsStates(StatesGroup):
    waiting_for_employee_number = State()
    waiting_for_employee_search = State()
    viewing_statistics = State()


# ====================== Вспомогательные функции ======================


async def show_statistics_list(message: Message, state: FSMContext, bot):
    """Отображает список сотрудников со статистикой нарушений

    :param message: Объект сообщения
    :param state: Состояние FSM
    :param bot: Объект бота
    """
    waiters = await sync_to_async(list)(
        Waiter.objects.order_by('last_name', 'first_name').all()
    )

    if not waiters:
        await message.answer("Список сотрудников пуст.", reply_markup=security_keyboard)
        return

    formatted_list = await get_formatted_employee_list(waiters)
    await message.answer(formatted_list, reply_markup=statistics_keyboard, parse_mode='HTML'
                         )
    await state.update_data(waiters=waiters)


async def handle_employee_search_request(message: Message, state: FSMContext):
    """Обрабатывает запрос на поиск сотрудника

    :param message: Объект сообщения
    :param state: Состояние FSM
    """
    await message.answer(
        "Введите имя или фамилию сотрудника для поиска:",
        reply_markup=back_keyboard
    )
    await state.set_state(StatisticsStates.waiting_for_employee_search)


async def process_search_results(message: Message, state: FSMContext, bot, search_query):
    """Обрабатывает результаты поиска сотрудников

    :param message: Объект сообщения
    :param state: Состояние FSM
    :param bot: Объект бота
    :param search_query: Поисковый запрос
    """
    waiters = await sync_to_async(list)(Waiter.objects.order_by('last_name', 'first_name').all())

    filtered_waiters = [
        w for w in waiters
        if search_query in w.last_name.lower() or
           search_query in w.first_name.lower() or
           (w.patronymic and search_query in w.patronymic.lower())
    ]

    if not filtered_waiters:
        await message.answer("Сотрудники по вашему запросу не найдены.", reply_markup=back_keyboard)
        return

    if len(filtered_waiters) == 1:
        await show_waiter_profile(message, filtered_waiters[0], bot)
        await state.set_state(StatisticsStates.viewing_statistics)
    else:
        now = datetime.now()
        current_month = now.strftime("%B").lower()

        employees_list = []
        for waiter in filtered_waiters:
            current_month_count = await sync_to_async(get_current_month_violations_count)(waiter)
            total_count = await sync_to_async(get_total_violations_count)(waiter)

            employees_list.append(
                f"{waiter.last_name} {waiter.first_name} {waiter.patronymic or ''} "
                f"({current_month_count} за {current_month}/всего {total_count})"
            )

        await message.answer(
            f"Найдено несколько сотрудников:\n\n" + "\n".join(employees_list) +
            "\n\nВведите более точное имя или фамилию",
            reply_markup=back_keyboard
        )


async def return_to_main_menu(message: Message, state: FSMContext):
    """Возвращает в главное меню

    :param message: Объект сообщения
    :param state: Состояние FSM
    """
    await state.clear()
    await message.answer(
        "Главное меню:",
        reply_markup=security_keyboard
    )


# ====================== Обработчики сообщений ======================

@router.message(F.text == "📊 Статистика")
async def handle_statistics(message: Message, state: FSMContext, bot):
    """Обработчик кнопки 'Статистика'"""
    await show_statistics_list(message, state, bot)
    await state.set_state(StatisticsStates.viewing_statistics)


@router.message(StatisticsStates.viewing_statistics, F.text == "🔍 Поиск сотрудника по имени")
async def handle_employee_search(message: Message, state: FSMContext):
    """Обработчик кнопки поиска сотрудника по имени"""
    await handle_employee_search_request(message, state)


@router.message(StatisticsStates.waiting_for_employee_search)
async def process_employee_search(message: Message, state: FSMContext, bot):
    """Обработка поиска сотрудника по имени"""
    if message.text.strip().lower() == "назад":
        await show_statistics_list(message, state, bot)
        await state.set_state(StatisticsStates.viewing_statistics)
        return

    await process_search_results(message, state, bot, message.text.strip().lower())


@router.message(StatisticsStates.viewing_statistics, F.text.regexp(r'^\d+$'))
async def process_employee_number(message: Message, state: FSMContext, bot):
    """Обработка выбора сотрудника по номеру"""
    await process_selected_employee_number(message, state, bot)


@router.message(StatisticsStates.viewing_statistics, F.text == "🔙 Назад")
async def handle_back_from_statistics(message: Message, state: FSMContext):
    """Обработчик кнопки 'Назад' в меню статистики"""
    await return_to_main_menu(message, state)
