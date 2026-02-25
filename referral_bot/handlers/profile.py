from aiogram import Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from keyboards.main import profile_kb
from handlers.button_helper import safe_edit_or_send

router = Router()


@router.callback_query(lambda c: c.data == "menu:profile")
async def cb_profile(callback: CallbackQuery, db_user: User) -> None:
    uname = f"@{db_user.username}" if db_user.username else "не указан"
    text = (
        "👤 <b>Профиль</b>\n\n"
        f"Имя: {db_user.first_name}\n"
        f"ID: <code>{db_user.user_id}</code>\n"
        f"Username: {uname}\n"
        f"Баланс: <b>{db_user.stars_balance:.2f} ⭐</b>\n"
        f"Рефералов: <b>{db_user.referrals_count}</b>"
    )
    await safe_edit_or_send(callback, text, profile_kb())
    await callback.answer()
