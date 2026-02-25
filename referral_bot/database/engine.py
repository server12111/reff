from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database.models import Base, BotSettings
from config import config

engine = create_async_engine("sqlite+aiosqlite:///bot.db", echo=False)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _seed_settings()


async def _seed_settings() -> None:
    """Insert default settings if they don't exist."""
    defaults = {
        "referral_reward": str(config.REFERRAL_REWARD),
        "bonus_cooldown_hours": str(config.BONUS_COOLDOWN_HOURS),
        "bonus_min": str(config.BONUS_MIN),
        "bonus_max": str(config.BONUS_MAX),
        "payments_channel_id": "",
        "payments_channel_url": "",
        # Games
        "game_football_enabled": "1",
        "game_football_coeff": "2.5",
        "game_football_min_bet": "1.0",
        "game_football_daily_limit": "0",
        "game_basketball_enabled": "1",
        "game_basketball_coeff": "1.25",
        "game_basketball_min_bet": "1.0",
        "game_basketball_daily_limit": "0",
        "game_bowling_enabled": "1",
        "game_bowling_coeff": "3.0",
        "game_bowling_min_bet": "1.0",
        "game_bowling_daily_limit": "0",
        "game_dice_enabled": "1",
        "game_dice_coeff": "1.5",
        "game_dice_min_bet": "1.0",
        "game_dice_daily_limit": "0",
        "game_slots_enabled": "1",
        "game_slots_coeff1": "6.0",
        "game_slots_coeff2": "2.0",
        "game_slots_min_bet": "1.0",
        "game_slots_daily_limit": "0",
    }
    async with SessionFactory() as session:
        for key, value in defaults.items():
            existing = await session.get(BotSettings, key)
            if existing is None:
                session.add(BotSettings(key=key, value=value))
        await session.commit()


async def get_setting(session: AsyncSession, key: str) -> str | None:
    row = await session.get(BotSettings, key)
    return row.value if row else None


async def set_setting(session: AsyncSession, key: str, value: str) -> None:
    row = await session.get(BotSettings, key)
    if row:
        row.value = value
    else:
        session.add(BotSettings(key=key, value=value))
    await session.commit()


async def get_button_content(session: AsyncSession, key: str):
    from database.models import ButtonContent
    return await session.get(ButtonContent, key)


async def set_button_photo(session: AsyncSession, key: str, photo_file_id: str | None) -> None:
    from database.models import ButtonContent
    row = await session.get(ButtonContent, key)
    if row:
        row.photo_file_id = photo_file_id
    else:
        session.add(ButtonContent(button_key=key, photo_file_id=photo_file_id))
    await session.commit()


async def set_button_text(session: AsyncSession, key: str, text: str | None) -> None:
    from database.models import ButtonContent
    row = await session.get(ButtonContent, key)
    if row:
        row.text = text
    else:
        session.add(ButtonContent(button_key=key, text=text))
    await session.commit()
