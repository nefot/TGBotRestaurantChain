# SecurityStaff/telegramBot/keyboards.py

# Клавиатура для службы безопасности
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Основная клавиатура безопасности


# Клавиатура управления сотрудниками
employees_management_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить сотрудника"), KeyboardButton(text="➖ Удалить сотрудника")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)


violations_management_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Добавить нарушение")],
        [KeyboardButton(text="🔍 Просмотр нарушений")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)
# Клавиатура для официантов
waiter_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📖 История нарушений")],
        [KeyboardButton(text="📊 Рейтинг"), KeyboardButton(text="👤 Мой профиль")]
    ],
    resize_keyboard=True
)

# Клавиатура для управления нарушениями
back_to_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 Назад")]],
    resize_keyboard=True
)

# Клавиатура для статистики
statistics_keyboard = ReplyKeyboardMarkup(
    keyboard=[
    [KeyboardButton(text="🔍 Поиск сотрудника по имени")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)

# Клавиатура с кнопкой "Назад"
back_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)

# Клавиатура для управления профилями
profile_management_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🆔 Мой профиль")],
        [KeyboardButton(text="👥 Профили сотрудников")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)

# Обновим security_keyboard, заменив старую кнопку
security_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Управление нарушениями")],
        [KeyboardButton(text="👤 Управление профилем")],
        [KeyboardButton(text="📊 Статистика")]
    ],
    resize_keyboard=True
)
