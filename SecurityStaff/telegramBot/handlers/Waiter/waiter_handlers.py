from aiogram import Router, F
from aiogram.types import Message

from .keybroads import main_keyboard
from .profile_router import router as profile_router
from .rang_router import router as rang_router
from .violation_router import router as violation_router

router = Router()

# Включаем роутеры напрямую, без .router
router.include_router(violation_router)
router.include_router(profile_router)
router.include_router(rang_router)


