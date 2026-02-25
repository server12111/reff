from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import get_button_content


async def answer_with_content(
    target: CallbackQuery | Message,
    session: AsyncSession,
    button_key: str,
    default_text: str,
    keyboard: InlineKeyboardMarkup,
) -> None:
    """Send response with optional photo+text configured by admin.

    If admin set a photo for this button — deletes current message and sends
    a new photo message with caption (admin text or default_text).
    If admin set only text — shows that text instead of default.
    If nothing is configured — shows default_text via edit_text.
    """
    content = await get_button_content(session, button_key)

    has_photo = bool(content and content.photo_file_id)
    text = (content.text if content and content.text else None) or default_text

    if has_photo:
        if isinstance(target, CallbackQuery):
            try:
                await target.message.delete()
            except Exception:
                pass
            await target.message.answer_photo(
                photo=content.photo_file_id,
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        else:
            await target.answer_photo(
                photo=content.photo_file_id,
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
    else:
        if isinstance(target, CallbackQuery):
            try:
                await target.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
            except Exception:
                try:
                    await target.message.delete()
                except Exception:
                    pass
                await target.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
        else:
            await target.answer(text, parse_mode="HTML", reply_markup=keyboard)


async def safe_edit_or_send(
    target: CallbackQuery | Message,
    text: str,
    keyboard: InlineKeyboardMarkup,
    parse_mode: str | None = "HTML",
) -> None:
    if isinstance(target, CallbackQuery):
        try:
            await target.message.edit_text(text, parse_mode=parse_mode, reply_markup=keyboard)
            return
        except Exception:
            try:
                await target.message.delete()
            except Exception:
                pass
            await target.message.answer(text, parse_mode=parse_mode, reply_markup=keyboard)
    else:
        await target.answer(text, parse_mode=parse_mode, reply_markup=keyboard)
