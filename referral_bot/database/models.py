from datetime import datetime
from sqlalchemy import BigInteger, String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str] = mapped_column(String(128))
    referrer_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.user_id"), nullable=True
    )
    stars_balance: Mapped[float] = mapped_column(Float, default=0.0)
    referrals_count: Mapped[int] = mapped_column(Integer, default=0)
    last_bonus_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    reward: Mapped[float] = mapped_column(Float, default=0.0)
    is_random: Mapped[bool] = mapped_column(Boolean, default=False)
    reward_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    reward_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    usage_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)  # None = unlimited
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PromoUse(Base):
    __tablename__ = "promo_uses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    promo_id: Mapped[int] = mapped_column(Integer, ForeignKey("promo_codes.id"))
    used_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Withdrawal(Base):
    __tablename__ = "withdrawals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending, approved, rejected
    channel_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payments_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class BotSettings(Base):
    """Runtime-configurable settings, editable via admin panel."""
    __tablename__ = "bot_settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_type: Mapped[str] = mapped_column(String(32))  # subscribe / referrals
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)
    reward: Mapped[float] = mapped_column(Float)
    target_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    channel_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TaskCompletion(Base):
    __tablename__ = "task_completions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"))
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class GameSession(Base):
    __tablename__ = "game_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"), index=True)
    game_type: Mapped[str] = mapped_column(String(32), index=True)
    bet: Mapped[float] = mapped_column(Float)
    result: Mapped[str] = mapped_column(String(8))   # "win" | "lose"
    payout: Mapped[float] = mapped_column(Float, default=0.0)
    played_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class ButtonContent(Base):
    """Photo and text configured by admin for each menu button."""
    __tablename__ = "button_contents"

    button_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    photo_file_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
