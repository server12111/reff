from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, BotSettings
from services.subgram import check_user, clear_cache
from keyboards.main import main_menu_kb, subgram_kb
from handlers.button_helper import answer_with_content
from config import config

router = Router()

MAIN_MENU_TEXT = (
    "\U0001F44B <b>\u0414\u043e\u0431\u0440\u043e \u043f\u043e\u0436\u0430\u043b\u043e\u0432\u0430\u0442\u044c \u0432 SrvNkStars!</b>\n\n"
    "\U0001F31F \u0417\u0430\u0440\u0430\u0431\u0430\u0442\u044b\u0432\u0430\u0439 Telegram Stars \u043f\u0440\u044f\u043c\u043e \u0437\u0434\u0435\u0441\u044c:\n\n"
    "\u2022 \u2B50 <b>\u0420\u0435\u0444\u0435\u0440\u0430\u043b\u044b</b> \u2014 \u043f\u0440\u0438\u0433\u043b\u0430\u0448\u0430\u0439 \u0434\u0440\u0443\u0437\u0435\u0439 \u0438 \u043f\u043e\u043b\u0443\u0447\u0430\u0439 \u0437\u0432\u0451\u0437\u0434\u044b \u0437\u0430 \u043a\u0430\u0436\u0434\u043e\u0433\u043e\n"
    "\u2022 \U0001F4CB <b>\u0417\u0430\u0434\u0430\u043d\u0438\u044f</b> \u2014 \u043f\u043e\u0434\u043f\u0438\u0441\u044b\u0432\u0430\u0439\u0441\u044f \u043d\u0430 \u043a\u0430\u043d\u0430\u043b\u044b \u0438 \u0432\u044b\u043f\u043e\u043b\u043d\u044f\u0439 \u0437\u0430\u0434\u0430\u0447\u0438\n"
    "\u2022 \U0001F3AE <b>\u0418\u0433\u0440\u044b</b> \u2014 \u0438\u0441\u043f\u044b\u0442\u0430\u0439 \u0443\u0434\u0430\u0447\u0443 \u0432 \u043c\u0438\u043d\u0438-\u0438\u0433\u0440\u0430\u0445\n"
    "\u2022 \U0001F381 <b>\u0411\u043e\u043d\u0443\u0441</b> \u2014 \u0431\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u044b\u0435 \u0437\u0432\u0451\u0437\u0434\u044b \u043a\u0430\u0436\u0434\u044b\u0435 24 \u0447\u0430\u0441\u0430\n"
    "\u2022 \U0001F4B0 <b>\u0412\u044b\u0432\u043e\u0434</b> \u2014 \u0432\u044b\u0432\u043e\u0434\u0438 \u043d\u0430\u043a\u043e\u043f\u043b\u0435\u043d\u043d\u043e\u0435 \u043d\u0430 \u0441\u0432\u043e\u0439 Telegram\n\n"
    "\u0412\u044b\u0431\u0435\u0440\u0438 \u0440\u0430\u0437\u0434\u0435\u043b \u043d\u0438\u0436\u0435 \U0001F447"
)

MAIN_MENU_TEXT_MENU = (
    "\U0001F44B <b>\u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e</b>\n\n"
    "\U0001F31F \u0417\u0430\u0440\u0430\u0431\u0430\u0442\u044b\u0432\u0430\u0439 Telegram Stars \u043f\u0440\u044f\u043c\u043e \u0437\u0434\u0435\u0441\u044c:\n\n"
    "\u2022 \u2B50 <b>\u0420\u0435\u0444\u0435\u0440\u0430\u043b\u044b</b> \u2014 \u043f\u0440\u0438\u0433\u043b\u0430\u0448\u0430\u0439 \u0434\u0440\u0443\u0437\u0435\u0439 \u0438 \u043f\u043e\u043b\u0443\u0447\u0430\u0439 \u0437\u0432\u0451\u0437\u0434\u044b \u0437\u0430 \u043a\u0430\u0436\u0434\u043e\u0433\u043e\n"
    "\u2022 \U0001F4CB <b>\u0417\u0430\u0434\u0430\u043d\u0438\u044f</b> \u2014 \u043f\u043e\u0434\u043f\u0438\u0441\u044b\u0432\u0430\u0439\u0441\u044f \u043d\u0430 \u043a\u0430\u043d\u0430\u043b\u044b \u0438 \u0432\u044b\u043f\u043e\u043b\u043d\u044f\u0439 \u0437\u0430\u0434\u0430\u0447\u0438\n"
    "\u2022 \U0001F3AE <b>\u0418\u0433\u0440\u044b</b> \u2014 \u0438\u0441\u043f\u044b\u0442\u0430\u0439 \u0443\u0434\u0430\u0447\u0443 \u0432 \u043c\u0438\u043d\u0438-\u0438\u0433\u0440\u0430\u0445\n"
    "\u2022 \U0001F381 <b>\u0411\u043e\u043d\u0443\u0441</b> \u2014 \u0431\u0435\u0441\u043f\u043b\u0430\u0442\u043d\u044b\u0435 \u0437\u0432\u0451\u0437\u0434\u044b \u043a\u0430\u0436\u0434\u044b\u0435 24 \u0447\u0430\u0441\u0430\n"
    "\u2022 \U0001F4B0 <b>\u0412\u044b\u0432\u043e\u0434</b> \u2014 \u0432\u044b\u0432\u043e\u0434\u0438 \u043d\u0430\u043a\u043e\u043f\u043b\u0435\u043d\u043d\u043e\u0435 \u043d\u0430 \u0441\u0432\u043e\u0439 Telegram\n\n"
    "\u0412\u044b\u0431\u0435\u0440\u0438 \u0440\u0430\u0437\u0434\u0435\u043b \u043d\u0438\u0436\u0435 \U0001F447"
)


async def _register_user(
    session: AsyncSession,
    user_id: int,
    username: str | None,
    first_name: str,
    referrer_id: int | None,
) -> tuple[User, bool, float]:
    """Returns (user, is_new, referral_reward_given)."""
    db_user = await session.get(User, user_id)
    if db_user is not None:
        db_user.username = username
        db_user.first_name = first_name
        await session.commit()
        return db_user, False, 0.0

    # New user — assign referrer only now
    valid_referrer = None
    if referrer_id and referrer_id != user_id:
        referrer = await session.get(User, referrer_id)
        if referrer:
            valid_referrer = referrer_id

    db_user = User(
        user_id=user_id,
        username=username,
        first_name=first_name,
        referrer_id=valid_referrer,
    )
    session.add(db_user)

    reward_given = 0.0
    if valid_referrer:
        referrer = await session.get(User, valid_referrer)
        if referrer:
            rr_row = await session.get(BotSettings, "referral_reward")
            reward_given = float(rr_row.value) if rr_row else config.REFERRAL_REWARD
            referrer.stars_balance += reward_given
            referrer.referrals_count += 1

    await session.commit()
    return db_user, True, reward_given


async def _do_subgram_and_open(
    target,  # Message or CallbackQuery
    session: AsyncSession,
    user_id: int,
    username: str | None,
    first_name: str,
    referrer_id: int | None = None,
    is_start: bool = False,
) -> None:
    """Run Subgram check, register if needed, then show main menu or sponsor wall."""
    tg_user = target.from_user if isinstance(target, CallbackQuery) else target.from_user
    result = await check_user(
        user_id=user_id,
        chat_id=user_id,  # private chats: chat_id == user_id
        first_name=first_name,
        username=username,
        language_code=getattr(tg_user, "language_code", None),
        is_premium=bool(getattr(tg_user, "is_premium", False)),
    )

    send = target.answer if isinstance(target, Message) else target.message.answer

    if result.status == "warning":
        await send(
            "📋 Для доступа к боту необходимо подписаться на наших спонсоров:",
            reply_markup=subgram_kb(result.sponsors),
        )
        if isinstance(target, CallbackQuery):
            await target.answer()
        return

    # ok or error ? give access
    if is_start:
        user, is_new, reward_given = await _register_user(session, user_id, username, first_name, referrer_id)
        if is_new and user.referrer_id:
            await send("👋 Добро пожаловать! Ты перешёл по реферальной ссылке.")
            # Push notification to referrer
            bot: Bot = target.bot if isinstance(target, Message) else target.message.bot
            try:
                await bot.send_message(
                    user.referrer_id,
                    f"🎉 Вам начислено <b>{reward_given} ⭐</b> за нового реферала!",
                    parse_mode="HTML",
                )
            except Exception:
                pass

    await answer_with_content(
        target=target,
        session=session,
        button_key="menu:main",
        default_text=MAIN_MENU_TEXT,
        keyboard=main_menu_kb(),
    )
    if isinstance(target, CallbackQuery):
        await target.answer()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    args = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    referrer_id = None
    if args.startswith("ref_"):
        try:
            referrer_id = int(args[4:])
        except ValueError:
            pass

    await _do_subgram_and_open(
        target=message,
        session=session,
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        referrer_id=referrer_id,
        is_start=True,
    )


@router.callback_query(lambda c: c.data == "subgram:check")
async def cb_subgram_check(callback: CallbackQuery, session: AsyncSession) -> None:
    await callback.message.delete()
    await _do_subgram_and_open(
        target=callback,
        session=session,
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        is_start=False,
    )


@router.callback_query(lambda c: c.data == "menu:main")
async def cb_main_menu(callback: CallbackQuery, session: AsyncSession) -> None:
    await answer_with_content(
        target=callback,
        session=session,
        button_key="menu:main",
        default_text=MAIN_MENU_TEXT_MENU,
        keyboard=main_menu_kb(),
    )
    await callback.answer()
