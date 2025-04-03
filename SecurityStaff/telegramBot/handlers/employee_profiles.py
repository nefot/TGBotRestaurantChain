import os
import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove
from asgiref.sync import sync_to_async
from django.conf import settings

from SecurityStaff.models import Waiter, ContactInfo, Post
from .service import validate_telegram_username, show_waiter_profile, get_formatted_employee_list, delete_employee
from ..keyboards import security_keyboard, employees_management_keyboard, violations_management_keyboard, profile_management_keyboard

router = Router()
PHONE_REGEX = r'^(\+7|8)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}$'
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


class AddEmployeeStates(StatesGroup):
    waiting_for_photo = State()
    waiting_for_last_name = State()
    waiting_for_first_name = State()
    waiting_for_patronymic = State()
    waiting_for_user_id = State()
    waiting_for_contact_info = State()
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_address = State()
    waiting_for_posts = State()


class DeleteEmployeeStates(StatesGroup):
    waiting_for_employee_number = State()


@router.message(F.text == "➕ Добавить сотрудника")
async def handle_add_employee(message: Message, state: FSMContext):
    """Обработчик кнопки добавления сотрудника"""
    await message.answer("Пожалуйста, отправьте фотографию сотрудника:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddEmployeeStates.waiting_for_photo)


@router.message(AddEmployeeStates.waiting_for_photo, F.content_type == "photo")
async def process_employee_photo(message: Message, state: FSMContext, bot):
    """Обработка фото сотрудника"""
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    await state.update_data(photo_file_path=file_path)
    await message.answer("Введите фамилию сотрудника:")
    await state.set_state(AddEmployeeStates.waiting_for_last_name)


@router.message(AddEmployeeStates.waiting_for_last_name)
async def process_last_name(message: Message, state: FSMContext):
    """Обработка фамилии сотрудника"""
    await state.update_data(last_name=message.text)
    await message.answer("Введите имя сотрудника:")
    await state.set_state(AddEmployeeStates.waiting_for_first_name)


@router.message(AddEmployeeStates.waiting_for_first_name)
async def process_first_name(message: Message, state: FSMContext):
    """Обработка имени сотрудника"""
    await state.update_data(first_name=message.text)
    await message.answer("Введите отчество сотрудника (если есть, или отправьте '-'):")
    await state.set_state(AddEmployeeStates.waiting_for_patronymic)


@router.message(AddEmployeeStates.waiting_for_patronymic)
async def process_patronymic(message: Message, state: FSMContext):
    """Обработка отчества сотрудника"""
    patronymic = message.text if message.text != '-' else ''
    await state.update_data(patronymic=patronymic)
    await message.answer("Введите тег сотрудника в Telegram, пример (@nefoter):")
    await state.set_state(AddEmployeeStates.waiting_for_user_id)


@router.message(AddEmployeeStates.waiting_for_user_id)
async def process_user_id(message: Message, state: FSMContext):
    """Обработка Telegram username сотрудника"""
    user_input = message.text.strip()

    # Валидация и получение ошибки (если есть)
    error = await validate_telegram_username(user_input)

    if error:
        await message.answer(error)
        return

    # Все проверки пройдены
    await state.update_data(user_id=user_input)
    await message.answer("✅ Username принят. Теперь введите номер телефона:")
    await state.set_state(AddEmployeeStates.waiting_for_phone)


@router.message(AddEmployeeStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Обработка номера телефона с валидацией"""
    phone = message.text.strip()

    if phone:
        if not re.match(PHONE_REGEX, phone):
            await message.answer("❌ Неверный формат телефона. Пожалуйста, введите номер в формате +79991234567 или "
                                 "89991234567")
            return

        cleaned_phone = re.sub(r'[^\d+]', '', phone)
        if cleaned_phone.startswith('8'):
            cleaned_phone = '+7' + cleaned_phone[1:]

        await state.update_data(phone=cleaned_phone)

    await message.answer("Введите email (необязательно, формат: example@domain.com):")
    await state.set_state(AddEmployeeStates.waiting_for_email)


@router.message(AddEmployeeStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    """Обработка email с валидацией"""
    email = message.text.strip()

    if email:
        if not re.match(EMAIL_REGEX, email):
            await message.answer("❌ Неверный формат email. Пожалуйста, введите email в формате example@domain.com")
            return

        await state.update_data(email=email.lower())

    await message.answer("Введите адрес (необязательно, минимум 5 символов):")
    await state.set_state(AddEmployeeStates.waiting_for_address)


@router.message(AddEmployeeStates.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    """Обработка адреса с базовой валидацией"""
    address = message.text.strip()

    if address:
        if len(address) < 5:
            await message.answer("❌ Адрес слишком короткий. Пожалуйста, введите минимум 5 символов")
            return

        await state.update_data(address=address)

    data = await state.get_data()
    contact_info = {
        'phone'  : data.get('phone', ''),
        'email'  : data.get('email', ''),
        'address': data.get('address', '')
    }
    await state.update_data(contact_info=contact_info)

    posts = await sync_to_async(list)(Post.objects.all())
    if posts:
        # Разбиваем список должностей на части по 20 записей
        posts_list = [f"{p.id}: {p.title}" for p in posts]
        chunk_size = 20
        for i in range(0, len(posts_list), chunk_size):
            chunk = posts_list[i:i + chunk_size]
            await message.answer("Доступные должности:\n" + "\n".join(chunk))

        await message.answer("Введите ID нужных должностей через запятую:")
    else:
        await message.answer("Нет доступных должностей. Сотрудник будет добавлен без должностей.")
        await state.update_data(posts=[])

    await state.set_state(AddEmployeeStates.waiting_for_posts)


@router.message(AddEmployeeStates.waiting_for_posts)
async def process_posts(message: Message, state: FSMContext, bot):
    """Обработка должностей и сохранение сотрудника"""
    try:
        data = await state.get_data()

        file_path = data['photo_file_path']
        photo = await bot.download_file(file_path)

        contact_info = await sync_to_async(ContactInfo.objects.create)(
            phone=data['contact_info']['phone'],
            email=data['contact_info']['email'],
            address=data['contact_info']['address']
        )

        waiter = await sync_to_async(Waiter.objects.create)(
            user_id=data['user_id'],
            last_name=data['last_name'],
            first_name=data['first_name'],
            patronymic=data.get('patronymic', ''),
            contact_info=contact_info
        )

        photo_path = f"waiters/images/{waiter.id}.jpg"
        full_path = os.path.join(settings.MEDIA_ROOT, photo_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'wb') as f:
            f.write(photo.read())

        waiter.image = photo_path
        await sync_to_async(waiter.save)()

        if message.text:
            try:
                post_ids = [int(id.strip()) for id in message.text.split(',')]
                posts = await sync_to_async(list)(Post.objects.filter(id__in=post_ids))
                if posts:
                    await sync_to_async(waiter.posts.set)(posts)
            except Exception:
                pass

        await message.answer(
            "✅ Сотрудник успешно добавлен!",
            reply_markup=employees_management_keyboard
        )
        await state.clear()

    except Exception as e:
        await message.answer(
            f"❌ Ошибка при добавлении сотрудника: {str(e)}",
            reply_markup=employees_management_keyboard
        )
        await state.clear()


@router.message(F.text == "➖ Удалить сотрудника")
async def handle_delete_employee(message: Message, state: FSMContext):
    """Обработчик кнопки удаления сотрудника"""

    waiters = await sync_to_async(list)(
        Waiter.objects.order_by('last_name', 'first_name')
        .select_related('contact_info')
        .prefetch_related('posts')
        .all()
    )
    if not waiters:
        await message.answer("Список сотрудников пуст.", reply_markup=employees_management_keyboard)
        return

    employees_list = await get_formatted_employee_list(waiters)
    await message.answer(
        f"{employees_list}\n\n"
        "Введите номер сотрудника для удаления:",
        reply_markup=ReplyKeyboardRemove(), parse_mode='HTML'
    )

    await state.update_data(waiters=waiters)
    await state.set_state(DeleteEmployeeStates.waiting_for_employee_number)


@router.message(DeleteEmployeeStates.waiting_for_employee_number)
async def process_delete_employee(message: Message, state: FSMContext):
    """Обработка номера сотрудника для удаления"""
    await delete_employee(message, state)


@router.message(F.text == "👥 Профили сотрудников")
async def handle_employee_profiles(message: Message, state: FSMContext):
    """Обработчик кнопки 'Профили сотрудников'."""

    waiters = await sync_to_async(list)(
        Waiter.objects.order_by('last_name', 'first_name')
        .select_related('contact_info')
        .prefetch_related('posts')
        .all()
    )

    if not waiters:
        await message.answer("Список сотрудников пуст.", reply_markup=employees_management_keyboard)
        return

    employees_list = await get_formatted_employee_list(waiters)

    await message.answer(
        employees_list + "\n\nВведите номер сотрудника для просмотра профиля:",
        reply_markup=employees_management_keyboard, parse_mode='HTML'

    )

    await state.update_data(waiters=waiters)


@router.message(F.text == "Назад")
async def handle_back_from_profiles(message: Message, state: FSMContext):
    """Обработчик кнопки 'Назад' в меню профилей."""
    await state.clear()
    await message.answer(
        "Главное меню:",
        reply_markup=profile_management_keyboard, parse_mode='HTML'

    )


@router.message(F.text.regexp(r'^\d+$'))
async def handle_employee_number(message: Message, state: FSMContext, bot):
    """Обработчик ввода номера сотрудника."""
    data = await state.get_data()
    waiters = data.get('waiters', [])

    try:
        number = int(message.text) - 1
        if 0 <= number < len(waiters):
            waiter = waiters[number]
            await show_waiter_profile(message, waiter, bot)
        else:
            await message.answer("Неверный номер сотрудника. Попробуйте снова.")
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
