# models/user.py
from sqlalchemy import BigInteger, String, DateTime, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class User(Base):
    __tablename__ = "users"

    # Asosiy autoincrement ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Telegram ID (foydalanuvchini aniqlash uchun)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, 
        unique=True,   # har bir user uchun yagona bo‘lishi kerak
        index=True,    # tezroq qidirish uchun index
        nullable=False # user Telegram_id har doim bo‘lishi shart
    )

    # Profil ma’lumotlari
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Qachon qo‘shilganini belgilash
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )

    # Bog‘lanishlar
    files = relationship(
        "File", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
