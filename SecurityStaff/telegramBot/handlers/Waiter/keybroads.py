from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# 1. Основная клавиатура (появляется при старте бота)

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Профиль сотрудника")],
            [KeyboardButton(text="📝 Просмотр нарушений")],
            [KeyboardButton(text="⭐ Рейтинговая система")]
        ],
        resize_keyboard=True,
        is_persistent=True,  # Клавиатура останется после использования
        input_field_placeholder="Выберите действие"
    )


main_keyboard = get_main_keyboard()

# 2. Клавиатура для violation_router
violation_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Исправлюсь")],
        [KeyboardButton(text="❌ Не согласен")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите вариант"
)

# 3. Клавиатура для profile_router
profile_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Личные данные")],
        [KeyboardButton(text="📜 История нарушений")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите раздел"
)

# Клавиатура "Назад" (может использоваться везде)
back_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)
