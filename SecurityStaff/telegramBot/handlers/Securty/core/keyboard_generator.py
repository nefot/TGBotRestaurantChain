# telegramBot/core/keyboard_generator.py
import os
import importlib.util
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from typing import Dict, Any, Optional, Union, Callable
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery


class KeyboardHandlerGenerator:
    def __init__(self, base_path: str, router: Router):
        self.base_path = base_path
        self.router = router
        self.handlers = {}

    async def load_handlers(self) -> Dict[str, Any]:
        """Рекурсивно загружает все обработчики из структуры папок"""
        return await self._process_directory(self.base_path, "")

    async def _process_directory(self, path: str, current_prefix: str) -> Dict[str, Any]:
        structure = {}
        for item in os.listdir(path):
            if item.startswith('__') or item.startswith('.'):
                continue

            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                # Формируем ключ для callback данных
                new_prefix = f"{current_prefix}_{item}" if current_prefix else item

                # Загружаем настройки кнопки
                settings = await self._load_button_settings(item_path, item)
                structure[item] = {
                    **settings,
                    "__path__"  : item_path,
                    "__prefix__": new_prefix
                }

                # Рекурсивно обрабатываем вложенные папки
                nested = await self._process_directory(item_path, new_prefix)
                if nested:
                    structure[item]["__children__"] = nested

                # Регистрируем обработчик для этой кнопки
                await self._register_handler(item_path, new_prefix, settings)

        return structure

    async def _load_button_settings(self, path: str, item: str) -> Dict[str, Any]:
        """Загружает настройки кнопки из __init__.py"""
        init_path = os.path.join(path, "__init__.py")
        settings = {
            "button_text"  : item,
            "auto_back"    : True,
            "row_width"    : 2,
            "keyboard_type": "reply"
        }

        if os.path.exists(init_path):
            spec = importlib.util.spec_from_file_location(f"{path}.__init__", init_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "button_settings"):
                settings.update(module.button_settings)

        return settings

    async def _register_handler(self, path: str, prefix: str, settings: Dict[str, Any]):
        """Регистрирует обработчик для кнопки"""
        handler_path = os.path.join(path, "handler.py")

        if os.path.exists(handler_path):
            # Динамически импортируем обработчик
            spec = importlib.util.spec_from_file_location(f"{path}.handler", handler_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Регистрируем стандартные обработчики
            if settings["keyboard_type"] == "reply":
                self.router.message.register(
                    self._create_reply_handler(prefix, module),
                    F.text == settings["button_text"]
                )
            else:
                self.router.callback_query.register(
                    self._create_inline_handler(prefix, module),
                    F.data == f"menu_{prefix}"
                )

            # Регистрируем кастомные обработчики из handler.py
            if hasattr(module, "register_handlers"):
                module.register_handlers(self.router)

    def _create_reply_handler(self, prefix: str, module: Any) -> Callable:
        """Создает обработчик для reply-кнопки"""

        async def handler(message: Message):
            if hasattr(module, "handle"):
                await module.handle(message)
            else:
                keyboard = await self.generate_keyboard(prefix)
                await message.answer(
                    f"Вы в разделе: {prefix.split('_')[-1]}",
                    reply_markup=keyboard
                )

        return handler

    def _create_inline_handler(self, prefix: str, module: Any) -> Callable:
        """Создает обработчик для inline-кнопки"""

        async def handler(callback: CallbackQuery):
            if hasattr(module, "handle"):
                await module.handle(callback)
            else:
                keyboard = await self.generate_keyboard(prefix)
                await callback.message.edit_text(
                    f"Вы в разделе: {prefix.split('_')[-1]}",
                    reply_markup=keyboard
                )
            await callback.answer()

        return handler

    async def generate_keyboard(self, prefix: str) -> Union[ReplyKeyboardBuilder, InlineKeyboardBuilder]:
        """Генерирует клавиатуру для указанного префикса"""
        # Находим нужный уровень в структуре
        current_level = self._find_level(prefix)

        if current_level["keyboard_type"] == "reply":
            builder = ReplyKeyboardBuilder()
        else:
            builder = InlineKeyboardBuilder()

        # Добавляем дочерние кнопки
        for name, data in current_level.get("__children__", {}).items():
            if data.get("hidden", False):
                continue

            if data["keyboard_type"] == "reply":
                builder.button(text=data["button_text"])
            else:
                builder.button(
                    text=data["button_text"],
                    callback_data=f"menu_{data['__prefix__']}"
                )

        # Добавляем кнопку "Назад" если требуется
        if current_level.get("auto_back", False):
            back_prefix = "_".join(prefix.split("_")[:-1]) if "_" in prefix else "root"

            if current_level["keyboard_type"] == "reply":
                builder.button(text="⬅️ Назад")
            else:
                builder.button(
                    text="⬅️ Назад",
                    callback_data=f"menu_{back_prefix}" if back_prefix != "root" else "menu_root"
                )

        # Применяем настройки расположения
        builder.adjust(*current_level.get("adjust", []), current_level.get("row_width", 2))

        return builder.as_markup() if current_level["keyboard_type"] == "reply" else builder

    def _find_level(self, prefix: str) -> Dict[str, Any]:
        """Находит уровень в структуре по префиксу"""
        parts = prefix.split("_")
        current = self.handlers
        for part in parts:
            if part in current:
                current = current[part]
            else:
                raise ValueError(f"Level {prefix} not found in structure")
        return current