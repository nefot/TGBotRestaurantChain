from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from asgiref.sync import sync_to_async

from SecurityStaff.models import Waiter, ViolationWaiter
from .employee_profiles import show_waiter_profile
from ..keyboards import security_keyboard, statistics_keyboard, back_keyboard

router = Router()


class StatisticsStates(StatesGroup):
    waiting_for_employee_search = State()


@router.message(F.text == "📊 Статистика")
async def handle_statistics(message: Message, state: FSMContext, bot):
    """Обработчик кнопки 'Статистика' - показывает список сотрудников и их нарушений"""

    waiters = await sync_to_async(list)(
        Waiter.objects.order_by('last_name', 'first_name').select_related('contact_info').prefetch_related(
            'posts').all()
    )

    if not waiters:
        await message.answer("Список сотрудников пуст.", reply_markup=security_keyboard)
        return


    employees_list = []
    for i, waiter in enumerate(waiters):

        violations_count = await sync_to_async(
            lambda: ViolationWaiter.objects.filter(waiter=waiter, role='Нарушитель').count()
        )()
        employees_list.append(
            f"{i + 1}. {waiter.last_name} {waiter.first_name} {waiter.patronymic or ''} "
            f"(нарушений: {violations_count})"
        )

    await message.answer(
        f"Список сотрудников (в алфавитном порядке):\n\n" + "\n".join(employees_list),
        reply_markup=statistics_keyboard
    )


@router.message(F.text == "🔍 Поиск сотрудника по имени")
async def handle_employee_search(message: Message, state: FSMContext):
    """Обработчик кнопки поиска сотрудника по имени"""
    await message.answer(
        "Введите имя или фамилию сотрудника для поиска:",
        reply_markup=back_keyboard
    )
    await state.set_state(StatisticsStates.waiting_for_employee_search)


@router.message(StatisticsStates.waiting_for_employee_search)
async def process_employee_search(message: Message, state: FSMContext, bot):
    """Обработка поиска сотрудника по имени с отображением профиля"""
    search_query = message.text.strip().lower()

    if search_query == "назад":
        await handle_back_from_statistics(message, state)
        return


    waiters = await sync_to_async(list)(
        Waiter.objects.order_by('last_name', 'first_name').select_related('contact_info').prefetch_related(
            'posts').all()
    )


    filtered_waiters = [
        w for w in waiters
        if search_query in w.last_name.lower() or
           search_query in w.first_name.lower() or
           (w.patronymic and search_query in w.patronymic.lower())
    ]

    if not filtered_waiters:
        await message.answer("Сотрудники по вашему запросу не найдены.", reply_markup=statistics_keyboard)
        await state.clear()
        return

    if len(filtered_waiters) == 1:

        await show_waiter_profile(message, filtered_waiters[0], bot)
    else:

        employees_list = []
        for waiter in filtered_waiters:
            violations_count = await sync_to_async(
                lambda: ViolationWaiter.objects.filter(waiter=waiter, role='Нарушитель').count()
            )()
            employees_list.append(
                f"{waiter.last_name} {waiter.first_name} {waiter.patronymic or ''} "
                f"(нарушений: {violations_count})"
            )

        await message.answer(
            f"Найдено несколько сотрудников:\n\n" + "\n".join(employees_list) +
            "\n\nВведите более точное имя или фамилию",
            reply_markup=back_keyboard
        )
        return

    await state.clear()


@router.message(F.text == "🔙 Назад")
async def handle_back_from_statistics(message: Message, state: FSMContext):
    """Обработчик кнопки 'Назад' в меню статистики"""
    await state.clear()
    await message.answer(
        "Главное меню:",
        reply_markup=security_keyboard
    )
