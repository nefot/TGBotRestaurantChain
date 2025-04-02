import os

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ContentType
from aiogram.types import Message, ReplyKeyboardRemove
from asgiref.sync import sync_to_async

from SecurityStaff.models import Violation, Waiter, ViolationType, ViolationStatus, ViolationWaiter
from src_tgbotrestaurantchain import settings
from ..keyboards import security_keyboard, violations_management_keyboard

router = Router()

from .violation_view import router as violation_view_router
from .employee_profiles import router as employee_profiles_router
from .statistics import router as statistics_router
from .profile_management import router as profile_management_router


router.include_router(profile_management_router)
router.include_router(employee_profiles_router)
router.include_router(violation_view_router)
router.include_router(statistics_router)


class AddViolationState(StatesGroup):
    waiting_for_photo = State()
    waiting_for_note = State()
    waiting_for_waiter = State()
    waiting_for_type = State()
    waiting_for_status = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "Добро пожаловать в систему учета нарушений!",
        reply_markup=security_keyboard
    )


@router.message(F.text == "📋 Управление нарушениями")
async def handle_violations_menu(message: Message):
    await message.answer(
        "Выберите действие с нарушениями:",
        reply_markup=violations_management_keyboard
    )


@router.message(F.text == "📝 Добавить нарушение")
async def start_add_violation(message: Message, state: FSMContext) -> None:
    """Инициирует процесс добавления нарушения, запрашивая фото.

    :param message: Входящее сообщение с командой
    :param state: Контекст состояния FSM
    """
    await message.answer(
        "Пожалуйста, отправьте фотографию нарушения:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddViolationState.waiting_for_photo)


@router.message(AddViolationState.waiting_for_photo, F.content_type == ContentType.PHOTO)
async def process_photo(message: Message, state: FSMContext, bot) -> None:
    """Обрабатывает фото нарушения и сохраняет его в media."""
    photo = message.photo[-1]


    file_ext = 'jpg'
    filename = f"violation_{message.message_id}.{file_ext}"
    media_path = os.path.join(settings.MEDIA_ROOT, 'violations/images', filename)


    os.makedirs(os.path.dirname(media_path), exist_ok=True)


    file = await bot.download(photo, destination=media_path)


    relative_path = os.path.join('violations/images', filename)
    await state.update_data(photo=relative_path)
    await message.answer("Теперь введите описание нарушения:")
    await state.set_state(AddViolationState.waiting_for_note)


@router.message(AddViolationState.waiting_for_note)
async def process_note(message: Message, state: FSMContext) -> None:
    """Обрабатывает описание нарушения и выводит нумерованный список официантов"""
    await state.update_data(note=message.text)

    waiters = await sync_to_async(list)(Waiter.objects.order_by('last_name', 'first_name').all())

    if not waiters:
        await message.answer("Нет доступных официантов в системе.")
        return

    # Формируем нумерованный список
    waiters_list = "\n".join([f"{i + 1}. {w.last_name} {w.first_name}" for i, w in enumerate(waiters)])

    await message.answer(
        f"Выберите номер официанта:\n\n{waiters_list}",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.update_data(waiters=waiters)  # Сохраняем список в состоянии
    await state.set_state(AddViolationState.waiting_for_waiter)
@router.message(AddViolationState.waiting_for_waiter)
async def process_waiter(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ФИО официанта и запрашивает тип нарушения.

    :param message: Сообщение с ФИО официанта в формате "Фамилия Имя"
    :param state: Текущее состояние FSM для сохранения данных
    :raises ValueError: Если введено некорректное ФИО
    :raises Waiter.DoesNotExist: Если официант не найден
    """

    try:
        data = await state.get_data()
        waiters = data['waiters']

        # Получаем номер из сообщения
        number = int(message.text.strip()) - 1  # -1 потому что список с 1

        if 0 <= number < len(waiters):
            waiter = waiters[number]
            await state.update_data(waiter=waiter)

            # Продолжаем процесс добавления нарушения
            types = await sync_to_async(list)(ViolationType.objects.all())
            types_list = "\n".join([f"{t.id}: {t.name}" for t in types])
            await message.answer(f"Введите ID типа нарушения:\n{types_list}")
            await state.set_state(AddViolationState.waiting_for_type)
        else:
            await message.answer("❌ Неверный номер. Пожалуйста, выберите номер из списка.")

    except ValueError:
        await message.answer("❌ Пожалуйста, введите число (номер официанта).")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

@router.message(AddViolationState.waiting_for_type)
async def process_type(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ID типа нарушения и запрашивает статус нарушения.

    :param message: Сообщение от пользователя с ID типа нарушения
    :param state: Текущее состояние FSM
    """
    try:
        type_id = int(message.text)
        violation_type = await sync_to_async(ViolationType.objects.get)(id=type_id)
        await state.update_data(violation_type=violation_type)

        statuses = await sync_to_async(list)(ViolationStatus.objects.all())
        statuses_list = "\n".join([f"{s.id}: {s.name}" for s in statuses])

        await message.answer(f"Введите ID статуса нарушения:\n{statuses_list}")
        await state.set_state(AddViolationState.waiting_for_status)
    except ValueError:
        await message.answer("Ошибка: Введите число.")
    except ViolationType.DoesNotExist:
        await message.answer("Ошибка: Тип нарушения не найден.")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")


@router.message(AddViolationState.waiting_for_status)
async def process_status(message: Message, state: FSMContext) -> None:
    """Обрабатывает статус нарушения и сохраняет полное нарушение в БД.

    :param message: Сообщение с ID статуса нарушения
    :param state: Контекст состояния FSM с данными нарушения
    :raises ValueError: Если введен некорректный ID статуса
    :raises ViolationStatus.DoesNotExist: Если статус не найден
    """
    try:
        status_id = int(message.text)
        data = await state.get_data()

        violation = Violation(
            image=data['photo'],
            note=data['note'],
            violation_type=data['violation_type'],
            status=await sync_to_async(ViolationStatus.objects.get)(id=status_id)
        )
        await sync_to_async(violation.save)()

        await sync_to_async(ViolationWaiter.objects.create)(
            violation=violation,
            waiter=data['waiter'],
            role='Нарушитель'
        )

        await message.answer("✅ Нарушение успешно добавлено!", reply_markup=security_keyboard)
        await state.clear()

    except ValueError:
        await message.answer("Ошибка: Введите числовой ID статуса")
        await state.clear()
    except ViolationStatus.DoesNotExist:
        await message.answer("Ошибка: Статус нарушения не найден")
        await state.clear()
    except Exception as e:
        await message.answer(f"Ошибка сохранения: {str(e)}")
        await state.clear()
