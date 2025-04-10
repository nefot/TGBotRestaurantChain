from datetime import datetime, timedelta

from asgiref.sync import sync_to_async

from SecurityStaff.models import ViolationWaiter


async def get_all_violations(waiter_id: int):
    """Получаем все нарушения для официанта"""
    return await sync_to_async(list)(
        ViolationWaiter.objects.filter(waiter_id=waiter_id)
        .select_related('violation', 'violation__status', 'violation__violation_type')
        .order_by('-violation__date')
    )


async def get_week_violations(waiter_id: int):
    """Получаем нарушения за последнюю неделю"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    return await sync_to_async(list)(
        ViolationWaiter.objects.filter(
            waiter_id=waiter_id,
            violation__date__range=[start_date, end_date]
        )
        .select_related('violation', 'violation__status', 'violation__violation_type')
        .order_by('-violation__date')
    )


async def format_violations_message(all_violations, week_violations):
    """Форматируем сообщение с нарушениями"""
    if not all_violations:
        return "У вас нет нарушений"

    # Формируем список всех нарушений
    all_violations_text = "## Нарушения\n\n" + "\n".join(
        f"{i + 1}. {vw.violation.violation_type.name} ({vw.violation.status.name})"
        for i, vw in enumerate(all_violations))

    # Формируем список нарушений за неделю
    week_violations_text = "\n\n## За неделю\n\n" + "\n".join(
        f"{i + 1}. {vw.violation.violation_type.name} ({vw.violation.status.name})"
        for i, vw in enumerate(week_violations))

    return all_violations_text + week_violations_text + "\n\nВыберите номер из списка для подробной информации"


async def get_violation_details(violation_waiter):
    """Получаем детали нарушения"""
    violation = violation_waiter.violation
    return (
        f"Нарушение #{violation.id}\n"
        f"Тип: {violation.violation_type.name}\n"
        f"Статус: {violation.status.name}\n"
        f"Дата: {violation.date.strftime('%d.%m.%Y')}\n"
        f"Описание: {violation.note or 'нет описания'}"
    )
