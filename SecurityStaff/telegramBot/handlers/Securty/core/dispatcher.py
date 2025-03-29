# telegramBot/core/dispatcher.py
from aiogram import Dispatcher, Router
from typing import Dict, Any
import os
import importlib.util


class DynamicDispatcher:
    def __init__(self, dp: Dispatcher, base_path: str):
        self.dp = dp
        self.base_path = base_path
        self.routers: Dict[str, Router] = {}

    async def register_handlers(self):
        """Рекурсивно ищет и регистрирует обработчики из всех папок"""
        await self._process_directory(self.base_path)

    async def _process_directory(self, path: str, parent_router):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                # Создаем роутер для текущего уровня
                router = Router()
                self.routers[item] = router

                if parent_router is not None:
                    parent_router.include_router(router)

                # Проверяем наличие handler.py
                handler_path = os.path.join(item_path, "handler.py")
                if os.path.exists(handler_path):
                    # Динамически импортируем модуль
                    spec = importlib.util.spec_from_file_location(f"{item}.handler", handler_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Регистрируем обработчики если они есть
                    if hasattr(module, "register_handlers"):
                        module.register_handlers(router)

                # Рекурсивно обрабатываем вложенные папки
                await self._process_directory(item_path, router)