import os
import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.types.callback_query import CallbackQuery
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from SecurityStaff.models import Waiter, ViolationWaiter, ContactInfo, Post
from .service_file import get_all_employees
from ..keyboards import security_keyboard, employees_management_keyboard

router = Router()
PHONE_REGEX = r'^(\+7|8)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}$'
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


# Состояния для добавления сотрудника
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
    waiting_for_employee_number = State()
    waiting_for_posts = State()


# Состояния для удаления сотрудника
class DeleteEmployeeStates(StatesGroup):
    waiting_for_employee_number = State()


@router.message(F.text == "➕ Добавить сотрудника")
async def handle_add_employee(message: Message, state: FSMContext):
    """Обработчик кнопки добавления сотрудника"""
    await message.answer(
        "Пожалуйста, отправьте фотографию сотрудника:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddEmployeeStates.waiting_for_photo)


@router.message(AddEmployeeStates.waiting_for_photo, F.content_type == "photo")
async def process_employee_photo(message: Message, state: FSMContext, bot):
    """Обработка фото сотрудника"""
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    # Сохраняем информацию о фото в состоянии
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
    """Обработка user_id сотрудника"""
    try:
        user_id = str(message.text)

        if user_id.split('')[0] != '@':
            await message.answer("тег должен начинаться с '@', пример (@nefoter)")
            return

        await state.update_data(user_id=user_id)

        await message.answer("Введите номер телефона")
        await state.set_state(AddEmployeeStates.waiting_for_phone)
    except ValueError as e:
        await message.answer(str(e))


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
        posts_list = "\n".join([f"{p.id}: {p.title}" for p in posts])
        await message.answer(f"Введите ID должностей через запятую:\n{posts_list}")
    else:
        await message.answer("Нет доступных должностей. Сотрудник будет добавлен без должностей.")
        await state.update_data(posts=[])

    await state.set_state(AddEmployeeStates.waiting_for_posts)


@router.message(AddEmployeeStates.waiting_for_posts)
async def process_posts(message: Message, state: FSMContext, bot):
    """Обработка должностей и сохранение сотрудника"""
    try:
        data = await state.get_data()

        # Скачиваем и сохраняем фото
        file_path = data['photo_file_path']
        photo = await bot.download_file(file_path)

        # Создаем контактную информацию
        contact_info = await sync_to_async(ContactInfo.objects.create)(
            phone=data['contact_info']['phone'],
            email=data['contact_info']['email'],
            address=data['contact_info']['address']
        )

        # Создаем сотрудника
        waiter = await sync_to_async(Waiter.objects.create)(
            user_id=data['user_id'],
            last_name=data['last_name'],
            first_name=data['first_name'],
            patronymic=data.get('patronymic', ''),
            contact_info=contact_info
        )

        # Сохраняем фото
        photo_path = f"waiters/images/{waiter.id}.jpg"
        full_path = os.path.join(settings.MEDIA_ROOT, photo_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'wb') as f:
            f.write(photo.read())

        waiter.image = photo_path
        await sync_to_async(waiter.save)()

        # Добавляем должности, если они указаны
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
    waiters = await sync_to_async(list)(Waiter.objects.order_by('last_name', 'first_name').all())

    if not waiters:
        await message.answer("Список сотрудников пуст.", reply_markup=employees_management_keyboard)
        return

    employees_list = "\n".join([f"{i + 1}. {w.last_name} {w.first_name}" for i, w in enumerate(waiters)])
    await message.answer(
        f"Список сотрудников:\n\n{employees_list}\n\n"
        "Введите номер сотрудника для удаления:",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.update_data(waiters=waiters)
    await state.set_state(DeleteEmployeeStates.waiting_for_employee_number)


@router.message(DeleteEmployeeStates.waiting_for_employee_number)
async def process_delete_employee(message: Message, state: FSMContext):
    """Обработка номера сотрудника для удаления"""
    try:
        data = await state.get_data()
        waiters = data['waiters']
        number = int(message.text) - 1

        if 0 <= number < len(waiters):
            waiter = waiters[number]

            # Удаляем связанные данные и самого сотрудника
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


PAGE_SIZE = 50  # Количество сотрудников на одной странице


async def get_violations_count(waiter: Waiter) -> int:
    """Возвращает количество нарушений для сотрудника"""
    return await sync_to_async(
        ViolationWaiter.objects.filter(waiter=waiter, role='Нарушитель').count
    )()


@router.message(F.text == "👥 Профили сотрудников")
async def handle_employee_profiles(message: Message, state: FSMContext):
    """Обработчик кнопки 'Профили сотрудников' с пагинацией"""
    all_waiters = await get_all_employees()

    if not all_waiters:
        await message.answer("Список сотрудников пуст.", reply_markup=employees_management_keyboard)
        return

    # Сохраняем всех сотрудников в состоянии
    await state.update_data({
        'all_waiters' : all_waiters,
        'current_page': 0,
        'waiters_dict': {i + 1: waiter for i, waiter in enumerate(all_waiters)}  # Словарь для быстрого доступа
    })

    # Отображаем первую страницу
    await show_employees_page(message, state)
    # Устанавливаем состояние ожидания выбора сотрудника
    await state.set_state(AddEmployeeStates.waiting_for_employee_number)


@router.message(AddEmployeeStates.waiting_for_employee_number, F.text.regexp(r'^\d+$'))
async def handle_employee_selection(message: Message, state: FSMContext):
    """Обработчик выбора сотрудника по номеру"""
    data = await state.get_data()
    waiters_dict = data.get('waiters_dict', {})

    try:
        employee_number = int(message.text)
        if employee_number not in waiters_dict:
            raise ValueError

        waiter = waiters_dict[employee_number]
        # Получаем полную информацию о сотруднике
        violations_count = await get_violations_count(waiter)
        posts = await sync_to_async(list)(waiter.posts.all())

        response_text = (
            f"👤 Профиль сотрудника:\n"
            f"ФИО: {waiter.last_name} {waiter.first_name} {waiter.patronymic or ''}\n"
            f"Должности: {', '.join(post.title for post in posts) if posts else 'Не указано'}\n"
            f"Нарушений: {violations_count}\n"
            f"Контакт: {waiter.contact_info.phone if waiter.contact_info else 'Не указан'}"
        )

        await message.answer(response_text, reply_markup=employees_management_keyboard)
        await state.clear()

    except ValueError:
        await message.answer("Неверный номер сотрудника. Пожалуйста, введите номер из списка:")


@router.message(AddEmployeeStates.waiting_for_employee_number)
async def handle_wrong_employee_input(message: Message):
    """Обработчик некорректного ввода номера"""
    await message.answer("Пожалуйста, введите только номер сотрудника из списка:")


async def show_employees_page(message, state: FSMContext):
    """Отображает страницу со списком сотрудников с правильной нумерацией"""
    data = await state.get_data()
    all_waiters = data.get('all_waiters', [])
    current_page = data.get('current_page', 0)
    total_pages = (len(all_waiters) + PAGE_SIZE - 1) // PAGE_SIZE

    # Вычисляем границы для текущей страницы
    start_idx = current_page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_waiters = all_waiters[start_idx:end_idx]

    # Формируем список сотрудников для текущей страницы
    employees_list = []
    for i, waiter in enumerate(page_waiters, start=1):
        global_number = start_idx + i  # Глобальный номер (1-based)
        violations_count = await get_violations_count(waiter)
        employees_list.append(
            f"{global_number}. {waiter.last_name} {waiter.first_name} {waiter.patronymic or ''} "
            f"(нарушений: {violations_count})"
        )

    # Создаем клавиатуру пагинации
    pagination_kb = InlineKeyboardMarkup(inline_keyboard=[])
    row_buttons = []

    # Добавляем кнопку "Назад" если нужно
    if current_page > 0:
        row_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_page"))

    # Добавляем кнопку "Вперед" если нужно
    if end_idx < len(all_waiters):
        row_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data="next_page"))

    if row_buttons:
        pagination_kb.inline_keyboard.append(row_buttons)

    # Добавляем номер страницы
    pagination_kb.inline_keyboard.append([
        InlineKeyboardButton(text=f"Страница {current_page + 1}/{total_pages}", callback_data="page_info")
    ])

    text = (
            f"Список сотрудников (всего: {len(all_waiters)}):\n\n" +
            "\n".join(employees_list) +
            "\n\nВведите номер сотрудника для просмотра профиля:"
    )

    if isinstance(message, CallbackQuery):
        await message.message.edit_text(text, reply_markup=pagination_kb)
        await message.answer()
    else:
        await message.answer(text, reply_markup=pagination_kb)


@router.callback_query(F.data.in_(["prev_page", "next_page"]))
async def handle_pagination(callback: CallbackQuery, state: FSMContext):
    """Обработчик переключения страниц"""
    data = await state.get_data()
    current_page = data.get('current_page', 0)

    if callback.data == "prev_page" and current_page > 0:
        await state.update_data(current_page=current_page - 1)
    elif callback.data == "next_page":
        all_waiters = data.get('all_waiters', [])
        if (current_page + 1) * PAGE_SIZE < len(all_waiters):
            await state.update_data(current_page=current_page + 1)

    await show_employees_page(callback, state)


@router.message(F.text == "🔙 Назад")
async def handle_back_from_profiles(message: Message, state: FSMContext):
    """Обработчик кнопки 'Назад' в меню профилей."""
    await state.clear()
    await message.answer(
        "Главное меню:",
        reply_markup=security_keyboard
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


async def show_waiter_profile(message: Message, waiter, bot):
    """Отображает профиль сотрудника с фото и количеством нарушений."""
    # Получаем информацию о сотруднике
    try:
        contact_info = await sync_to_async(lambda: waiter.contact_info)()
        phone = contact_info.phone if contact_info else 'не указан'
        email = contact_info.email if contact_info else 'не указан'
    except ObjectDoesNotExist:
        phone = 'не указан'
        email = 'не указан'

    posts = await sync_to_async(lambda: list(waiter.posts.all()))()
    post_titles = ', '.join([post.title for post in posts]) if posts else 'не указаны'

    violations_count = await sync_to_async(
        lambda: ViolationWaiter.objects.filter(waiter=waiter, role='Нарушитель').count()
    )()

    profile_info = (
        f"👤 ФИО: {waiter.last_name} {waiter.first_name} {waiter.patronymic or ''}\n"
        f"📞 Контакты: {phone}\n"
        f"📧 Email: {email}\n"
        f"💼 Должности: {post_titles}\n"
        f"🚨 Количество нарушений: {violations_count}"
    )

    # Обработка фото
    try:
        if waiter.image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(waiter.image))

            if os.path.exists(image_path):
                # Читаем файл и создаем BufferedInputFile
                with open(image_path, 'rb') as photo_file:
                    photo_bytes = photo_file.read()

                # Создаем объект для отправки фото
                photo = BufferedInputFile(
                    file=photo_bytes,
                    filename=os.path.basename(image_path))

                # Отправляем фото с подписью
                await message.answer_photo(
                    photo=photo,
                    caption=profile_info,
                    reply_markup=employees_management_keyboard
                )
                return
            else:
                profile_info += "\n\n⚠️ Фото сотрудника не найдено на сервере"
        else:
            profile_info += "\n\n⚠️ Фото сотрудника отсутствует"
    except Exception as e:
        profile_info += f"\n\n⚠️ Ошибка при загрузке фото: {str(e)}"

    # Если фото нет или произошла ошибка, отправляем только текст
    await message.answer(
        profile_info,
        reply_markup=employees_management_keyboard
    )
