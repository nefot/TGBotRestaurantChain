import asyncio
import os
import types
from datetime import datetime
from typing import Optional

from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from aiogram.types import Message
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from SecurityStaff.models import Waiter, ViolationWaiter
from ..keyboards import employees_management_keyboard


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


async def get_contact_info(waiter, field: str):
    """Универсальная функция для получения контактной информации"""
    try:
        contact_info = await sync_to_async(lambda: waiter.contact_info)()
        if contact_info:
            value = getattr(contact_info, field, None)
            return value if value else 'не указан'
        return 'не указан'
    except ObjectDoesNotExist:
        return 'не указан'


async def load_waiter_image(waiter, info: str, message: Message):
    """Загрузка и отправка фото сотрудника"""
    try:
        if not waiter.image:
            return info + "\n\n⚠️ Фото сотрудника отсутствует"

        image_path = os.path.join(settings.MEDIA_ROOT, str(waiter.image))

        if not os.path.exists(image_path):
            return info + "\n\n⚠️ Фото сотрудника не найдено на сервере"

        with open(image_path, 'rb') as photo_file:
            photo_bytes = photo_file.read()

        photo = BufferedInputFile(
            file=photo_bytes,
            filename=os.path.basename(image_path)
        )

        await message.answer_photo(
            photo=photo,
            caption=info,
            reply_markup=employees_management_keyboard
        )
        return None  # Фото отправлено отдельным сообщением

    except Exception as e:
        return info + f"\n\n⚠️ Ошибка при загрузке фото: {str(e)}"


async def show_waiter_profile(message: Message, waiter, bot):
    """Отображение профиля сотрудника"""
    # Получаем все данные асинхронно параллельно
    phone, email, posts, violations = await asyncio.gather(
        get_contact_info(waiter, 'phone'),
        get_contact_info(waiter, 'email'),
        current_post(waiter),
        current_violation(waiter)
    )

    profile_info = (
        f"👤 ФИО: {waiter.last_name} {waiter.first_name} {waiter.patronymic or ''}\n"
        f"📞 Контакты: {phone}\n"
        f"📧 Email: {email}\n"
        f"💼 Должности: {posts}\n"
        f"🚨 Нарушения: {violations}"
    )

    # Пытаемся отправить фото
    remaining_info = await load_waiter_image(waiter, profile_info, message)

    # Если фото не было отправлено (ошибка или отсутствует), отправляем текстовую информацию
    if remaining_info is not None:
        await message.answer(
            remaining_info,
            reply_markup=employees_management_keyboard
        )


async def current_violation(waiter):
    """Получение информации о нарушениях"""
    now = datetime.now()
    month_translation = {
        'january': 'январь', 'february': 'февраль', 'march': 'март',
        'april'  : 'апрель', 'may': 'май', 'june': 'июнь',
        'july'   : 'июль', 'august': 'август', 'september': 'сентябрь',
        'october': 'октябрь', 'november': 'ноябрь', 'december': 'декабрь'
    }

    current_month = month_translation.get(now.strftime("%B").lower(), "текущий месяц")
    current_count, total_count = await asyncio.gather(
        sync_to_async(get_current_month_violations_count)(waiter),
        sync_to_async(get_total_violations_count)(waiter)
    )

    return f"({current_count} за {current_month}/всего {total_count})"


async def current_post(waiter):
    """Получение списка должностей"""
    try:
        posts = await sync_to_async(lambda: list(waiter.posts.all()))()
        return ', '.join(post.title for post in posts) if posts else 'не указаны'
    except Exception:
        return 'не указаны'


async def get_formatted_employee_list(waiters):
    """Форматирует список сотрудников для отображения"""

    name_lengths = [len(f"{w.last_name} {w.first_name} {w.patronymic or ''}") for w in waiters]
    max_length = max(name_lengths)

    employees_list = []
    for i, waiter in enumerate(waiters):
        full_name = f"{waiter.last_name} {waiter.first_name} {waiter.patronymic or ''}"
        padding = " " * (max_length - len(full_name) + 3)

        employees_list.append(
            f"{i + 1}. <b>{full_name}{padding}</b> <i>{await current_violation(waiter)}</i>"
        )

    return "Список сотрудников (в алфавитном порядке):\n\n" + "\n".join(employees_list)


async def delete_employee(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        waiters = data['waiters']
        number = int(message.text) - 1

        if 0 <= number < len(waiters):
            waiter = waiters[number]

            await sync_to_async(waiter.delete)()

            await message.answer(
                "✅ Сотрудник успешно удалён!",
                reply_markup=employees_management_keyboard
            )
        else:
            await message.answer(
                "Неверный номер сотрудника.",
                reply_markup=employees_management_keyboard
            )

        await state.clear()
    except ValueError:
        await message.answer(
            "Пожалуйста, введите число.",
            reply_markup=employees_management_keyboard
        )
        await state.clear()
    except Exception as e:
        await message.answer(
            f"❌ Ошибка при удалении сотрудника: {str(e)}",
            reply_markup=employees_management_keyboard
        )
        await state.clear()


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


async def validate_telegram_username(username: str) -> Optional[str]:
    """Валидация Telegram username

    Args:
        username: Введённый username для проверки

    Returns:
        str: Текст ошибки или None, если валидация пройдена
    """
    # Проверка минимальной длины
    if len(username) < 5:
        return "Username должен содержать минимум 5 символов (включая @)"

    # Проверка формата
    if not username.startswith('@'):
        return (
            "Username должен начинаться с '@'. Пример: @nefoter\n"
            "Пожалуйста, введите корректный username:"
        )

    # Проверка допустимых символов
    username_part = username[1:]  # часть без @
    if not username_part.replace('_', '').isalnum():
        return (
            "Username может содержать только буквы, цифры и подчеркивания.\n"
            "Пример правильного формата: @nefoter123\n"
            "Пожалуйста, введите корректный username:"
        )

    # Проверка максимальной длины
    if len(username) > 32:
        return (
            "Username слишком длинный (максимум 32 символа).\n"
            "Пожалуйста, введите корректный username:"
        )

    # Проверка уникальности в базе
    if await sync_to_async(Waiter.objects.filter(user_id=username).exists)():
        return (
            "Сотрудник с таким username уже существует.\n"
            "Пожалуйста, введите другой username:"
        )

    return None


async def prepare_violation_message(violation):
    """Подготавливает текст сообщения о нарушении и данные фото"""
    waiter = await sync_to_async(lambda: violation.violation_waiters.first().waiter)()

    text = (
        f"🔍 Нарушение #{violation.id}\n"
        f"👤 Сотрудник: {waiter.last_name} {waiter.first_name}\n"
        f"📅 Дата: {violation.date.strftime('%d.%m.%Y')}\n"
        f"🚨 Тип: {violation.violation_type.name}\n"
        f"📝 Описание: {violation.note}\n"
        f"🔒 Статус: {violation.status.name}"
    )

    photo = None
    error_message = None

    if violation.image:
        image_path = os.path.join(settings.MEDIA_ROOT, str(violation.image))
        if os.path.exists(image_path):
            try:
                photo = types.BufferedInputFile.from_file(
                    path=image_path,
                    filename=os.path.basename(image_path)
                )
            except Exception as e:
                error_message = f"⚠️ Ошибка при загрузке фото: {str(e)}"
        else:
            error_message = "⚠️ Фото не найдено на сервере"
    else:
        error_message = "⚠️ Фото отсутствует"

    return {
        "text": text,
        "photo": photo,
        "error_message": error_message
    }