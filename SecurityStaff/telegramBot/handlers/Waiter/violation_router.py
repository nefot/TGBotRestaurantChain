from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from asgiref.sync import sync_to_async

from SecurityStaff.models import ViolationWaiter
from .keybroads import back_keyboard
from ..service import prepare_violation_message

router = Router()


class ViolationStates(StatesGroup):
    viewing_list = State()
    viewing_details = State()


async def get_all_violations(waiter_id: int):
    """Получаем все нарушения для официанта"""
    return await sync_to_async(list)(
        ViolationWaiter.objects.filter(waiter_id=waiter_id)
        .select_related('violation', 'violation__status', 'violation__violation_type')
        .order_by('-violation__date')
    )


async def get_week_violations(waiter_id: int):
    """Получаем нарушения за последнюю неделю"""
    from datetime import datetime, timedelta
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


async def format_violations_list(all_violations, week_violations):
    """Форматирует список нарушений"""
    if not all_violations:
        return "У вас нет нарушений"

    all_text = "## Нарушения\n\n" + "\n".join(
        f"{i + 1}. {vw.violation.violation_type.name} ({vw.violation.status.name})"
        for i, vw in enumerate(all_violations))

    week_text = "\n\n## За неделю\n\n" + "\n".join(
        f"{i + 1}. {vw.violation.violation_type.name} ({vw.violation.status.name})"
        for i, vw in enumerate(week_violations))

    return all_text + week_text + "\n\nВыберите номер из списка для подробной информации"


@router.message(F.text == "📝 Просмотр нарушений")
async def start_view_violations(message: Message, state: FSMContext, waiter):
    all_violations = await get_all_violations(waiter.id)
    week_violations = await get_week_violations(waiter.id)

    violations_text = await format_violations_list(all_violations, week_violations)

    await state.update_data({
        'all_violations' : all_violations,
        'week_violations': week_violations
    })
    await state.set_state(ViolationStates.viewing_list)

    await message.answer(
        violations_text,
        reply_markup=back_keyboard
    )


@router.message(ViolationStates.viewing_list, F.text.regexp(r'^\d+$'))
async def show_selected_violation(message: Message, state: FSMContext):
    data = await state.get_data()
    all_violations = data.get('all_violations', [])

    try:
        num = int(message.text) - 1
        if 0 <= num < len(all_violations):
            violation_data = await prepare_violation_message(all_violations[num].violation)

            if violation_data['photo']:
                await message.answer_photo(
                    photo=violation_data['photo'],
                    caption=violation_data['text'],
                    reply_markup=back_keyboard
                )
            else:
                text = violation_data['text']
                if violation_data['error_message']:
                    text += f"\n\n{violation_data['error_message']}"
                await message.answer(text, reply_markup=back_keyboard)

            await state.set_state(ViolationStates.viewing_details)
        else:
            await message.answer("Неверный номер нарушения", reply_markup=back_keyboard)
    except ValueError:
        await message.answer("Пожалуйста, введите число", reply_markup=back_keyboard)


@router.message(F.text == "🔙 Назад")
async def back_to_main(message: Message, state: FSMContext):
    from .keybroads import main_keyboard
    await state.clear()
    await message.answer(
        "Главное меню:",
        reply_markup=main_keyboard
    )
