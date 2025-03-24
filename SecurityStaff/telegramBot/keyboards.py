# SecurityStaff/telegramBot/keyboards.py

# Клавиатура для службы безопасности
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Основная клавиатура безопасности
security_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Управление нарушениями")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="👥 Профили сотрудников")]
    ],
    resize_keyboard=True
)

# Клавиатура управления сотрудниками
employees_management_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить сотрудника"), KeyboardButton(text="➖ Удалить сотрудника")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)
security_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Управление нарушениями")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="👥 Профили сотрудников")]
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
security_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Управление нарушениями")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="👥 Профили сотрудников")]
    ],
    resize_keyboard=True
)
