from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async

from SecurityStaff.models import ViolationWaiter


def get_current_month_violations_count(waiter):
    """Возвращает количество нарушений за текущий месяц

    :param waiter: Объект сотрудника
    :return: Количество нарушений
    """
    now = datetime.now()
    return ViolationWaiter.objects.filter(
        waiter=waiter,
        role='Нарушитель',
        violation__date__month=now.month,
        violation__date__year=now.year
    ).count()


def get_total_violations_count(waiter):
    """Возвращает общее количество нарушений

    :param waiter: Объект сотрудника
    :return: Общее количество нарушений
    """
    return ViolationWaiter.objects.filter(
        waiter=waiter,
        role='Нарушитель'
    ).count()


async def get_formatted_employee_list(waiters):
    """Форматирует список сотрудников для отображения

    :param waiters: Список сотрудников
    :return: Отформатированный текст со списком
    """
    now = datetime.now()
    current_month = now.strftime("%B").lower()

    employees_list = []
    for i, waiter in enumerate(waiters):
        current_month_count = await sync_to_async(get_current_month_violations_count)(waiter)
        total_count = await sync_to_async(get_total_violations_count)(waiter)

        employees_list.append(
            f"{i + 1}. {waiter.last_name} {waiter.first_name} {waiter.patronymic or ''} "
            f"({current_month_count} за {current_month}/всего {total_count})"
        )

    return "Список сотрудников (в алфавитном порядке):\n\n" + "\n".join(employees_list)


async def process_selected_employee_number(message: Message, state: FSMContext, bot):
    """Обрабатывает выбор сотрудника по номеру

    :param message: Объект сообщения
    :param state: Состояние FSM
    :param bot: Объект бота
    """
    data = await state.get_data()
    waiters = data.get('waiters', [])

    try:
        number = int(message.text.strip()) - 1
        if 0 <= number < len(waiters):
            waiter = waiters[number]
            from SecurityStaff.telegramBot.handlers.employee_profiles import show_waiter_profile
            await show_waiter_profile(message, waiter, bot)
        else:
            await message.answer("Неверный номер сотрудника. Попробуйте снова.")
    except ValueError:
        await message.answer("Пожалуйста, введите число (номер сотрудника).")


