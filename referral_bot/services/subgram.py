import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import aiohttp

from config import config

logger = logging.getLogger(__name__)

SUBGRAM_URL = "https://api.subgram.org/get-sponsors"
CACHE_HOURS = 24
REQUEST_TIMEOUT = 10  # seconds


@dataclass
class SubgramResult:
    status: str          # "ok" | "warning" | "error"
    sponsors: list[dict] = field(default_factory=list)


# In-memory cache: user_id → datetime of last successful "ok"
_cache: dict[int, datetime] = {}


def _is_cached(user_id: int) -> bool:
    ts = _cache.get(user_id)
    if ts is None:
        return False
    return datetime.utcnow() - ts < timedelta(hours=CACHE_HOURS)


def _set_cached(user_id: int) -> None:
    _cache[user_id] = datetime.utcnow()


def clear_cache(user_id: int) -> None:
    """Force re-check on next request (e.g. after /start)."""
    _cache.pop(user_id, None)


async def check_user(
    user_id: int,
    chat_id: int,
    first_name: str,
    username: str | None = None,
    language_code: str | None = None,
    is_premium: bool = False,
) -> SubgramResult:
    """
    Check user via Subgram API.
    Returns SubgramResult with status "ok", "warning" or "error".
    Caches successful checks for CACHE_HOURS hours.
    If SUBGRAM_TOKEN is not configured, always returns "ok".
    """
    if not config.SUBGRAM_TOKEN:
        return SubgramResult(status="ok")

    if _is_cached(user_id):
        return SubgramResult(status="ok")

    payload = {
        "user_id":       user_id,
        "chat_id":       chat_id,
        "first_name":    first_name,
        "username":      username or "",
        "language_code": language_code or "en",
        "is_premium":    is_premium,
    }
    headers = {"Auth": config.SUBGRAM_TOKEN}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                SUBGRAM_URL,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            ) as resp:
                if resp.status != 200:
                    logger.error(
                        "Subgram API returned HTTP %s for user %s", resp.status, user_id
                    )
                    return SubgramResult(status="error")

                data = await resp.json(content_type=None)

    except asyncio.TimeoutError:
        logger.error("Subgram API timeout for user %s", user_id)
        return SubgramResult(status="error")
    except aiohttp.ClientError as e:
        logger.error("Subgram API connection error for user %s: %s", user_id, e)
        return SubgramResult(status="error")
    except Exception as e:
        logger.error("Subgram API unexpected error for user %s: %s", user_id, e)
        return SubgramResult(status="error")

    status = data.get("status", "error")
    # Subgram returns sponsors under "data" key
    raw_sponsors = data.get("data", [])

    # Normalise sponsor objects to {"name": ..., "link": ...}
    sponsors = []
    for sp in raw_sponsors:
        sponsors.append({
            "name": sp.get("name") or sp.get("title") or "Подписаться",
            "link": sp.get("link") or sp.get("url") or "",
        })

    if status == "ok":
        _set_cached(user_id)
        logger.info("Subgram OK for user %s", user_id)
    elif status == "warning":
        logger.info("Subgram WARNING for user %s — %d sponsors", user_id, len(sponsors))
    else:
        logger.error("Subgram ERROR response for user %s: %s", user_id, data)

    return SubgramResult(status=status, sponsors=sponsors)
