# SecurityStaff/telegramBot/keyboards.py

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура для службы безопасности
security_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Управление нарушениями")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="👥 Профили сотрудников")]
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
violations_management_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Добавить нарушение")],
        [KeyboardButton(text="🔍 Просмотр нарушений")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)