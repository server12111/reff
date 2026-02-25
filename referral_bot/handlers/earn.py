from aiogram import Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import User
from keyboards.main import back_to_menu_kb
from handlers.button_helper import safe_edit_or_send
from config import config

router = Router()


@router.callback_query(lambda c: c.data == "menu:earn")
async def cb_earn(callback: CallbackQuery, session: AsyncSession, db_user: User) -> None:
    ref_link = f"https://t.me/{config.BOT_USERNAME}?start=ref_{db_user.user_id}"
    await safe_edit_or_send(
        callback,
        "⭐ <b>Заработать звёзды</b>\n\n"
        "Приглашай друзей и получай <b>Telegram Stars</b> за каждого нового участника!\n\n"
        "💰 <b>Сколько платим:</b>\n"
        "• За каждого реферала — <b>4–6 ⭐</b>\n"
        "• Один пользователь засчитывается только один раз\n"
        "• Выплата мгновенная — сразу после регистрации друга\n\n"
        "📤 <b>Как пригласить:</b>\n"
        "Отправь ссылку другу в личку, в чат или опубликуй в социальных сетях\n\n"
        f"🔗 <b>Твоя реферальная ссылка:</b>\n<code>{ref_link}</code>",
        back_to_menu_kb(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "menu:referrals")
async def cb_referrals(callback: CallbackQuery, session: AsyncSession, db_user: User) -> None:
    result = await session.execute(
        select(User).where(User.referrer_id == db_user.user_id)
    )
    refs = result.scalars().all()

    lines = []
    for ref in refs[:20]:
        name = ref.first_name or "—"
        uname = f"@{ref.username}" if ref.username else ""
        lines.append(f"• {name} {uname}")

    body = "\n".join(lines) if lines else "Рефералов пока нет."
    text = (
        f"👥 <b>Мои рефералы</b>\n\n"
        f"Всего: <b>{db_user.referrals_count}</b>\n\n"
        f"{body}"
    )
    await safe_edit_or_send(callback, text, back_to_menu_kb())
    await callback.answer()


