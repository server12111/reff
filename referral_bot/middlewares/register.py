from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from database.engine import SessionFactory
from config import config

# Callbacks/commands that manage their own subgram check — skip middleware for them
_SUBGRAM_SKIP_CALLBACKS = {"subgram:check"}
_SUBGRAM_SKIP_COMMANDS = {"/start", "/admin"}


class SessionMiddleware(BaseMiddleware):
    """Injects async DB session into every handler."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with SessionFactory() as session:
            data["session"] = session
            return await handler(event, data)


class SubgramMiddleware(BaseMiddleware):
    """
    Enforces Subgram subscription check before any bot feature.
    /start and subgram:check are whitelisted — they manage the check themselves.
    Admins bypass the check entirely.
    Successful verifications are cached in-memory for 24 hours.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        from services.subgram import check_user
        from keyboards.main import subgram_kb

        if isinstance(event, Message):
            user = event.from_user
            chat_id = event.chat.id
            text = event.text or ""
            # Whitelist: /start handles subgram itself
            if any(text.startswith(cmd) for cmd in _SUBGRAM_SKIP_COMMANDS):
                return await handler(event, data)
            send = event.answer
            answer_cb = None

        elif isinstance(event, CallbackQuery):
            user = event.from_user
            chat_id = event.message.chat.id
            # Whitelist: subgram:check handles verification itself
            if event.data in _SUBGRAM_SKIP_CALLBACKS:
                return await handler(event, data)
            send = event.message.answer
            answer_cb = event.answer

        else:
            return await handler(event, data)

        if user is None:
            return await handler(event, data)

        # Admins bypass subgram
        if user.id in config.ADMIN_IDS:
            return await handler(event, data)

        result = await check_user(
            user_id=user.id,
            chat_id=chat_id,
            first_name=user.first_name,
            username=user.username,
            language_code=getattr(user, "language_code", None),
            is_premium=bool(getattr(user, "is_premium", False)),
        )

        if result.status == "ok":
            return await handler(event, data)

        # Must answer callback query before sending a new message
        if answer_cb:
            try:
                await answer_cb()
            except Exception:
                pass

        if result.status == "warning":
            await send(
                "📋 Для доступа к боту необходимо подписаться на наших спонсоров:",
                reply_markup=subgram_kb(result.sponsors),
            )
        else:  # error
            await send("⚠️ Временно недоступна проверка подписки. Попробуйте позже.")


class RegisteredUserMiddleware(BaseMiddleware):
    """
    Blocks unregistered users from using the bot without /start.
    Admins always bypass this check.
    """

    SKIP_TEXT = {"/start", "/admin"}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        from database.models import User

        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        else:
            return await handler(event, data)

        if user is None:
            return

        # Admins bypass all checks
        if user.id in config.ADMIN_IDS:
            session = data.get("session")
            if session:
                db_user = await session.get(User, user.id)
                if db_user:
                    data["db_user"] = db_user
            return await handler(event, data)

        # Skip /start and /admin for regular users too
        if isinstance(event, Message):
            text = event.text or ""
            if any(text.startswith(cmd) for cmd in self.SKIP_TEXT):
                return await handler(event, data)

        session = data.get("session")
        if session is None:
            return await handler(event, data)

        db_user = await session.get(User, user.id)
        if db_user is None:
            if isinstance(event, Message):
                await event.answer("Нажми /start чтобы начать.")
            elif isinstance(event, CallbackQuery):
                await event.answer("Сначала нажми /start.", show_alert=True)
            return

        data["db_user"] = db_user
        return await handler(event, data)
