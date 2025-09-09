from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User

router = Router()

@router.message(CommandStart())
async def start_cmd(message: Message, session: AsyncSession):
    # Foydalanuvchini telegram_id bo‘yicha qidiramiz
    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()

    # Agar topilmasa, yangi yozuv qo‘shamiz
    if not user:
        user = User(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name or "",
            username=message.from_user.username or ""
        )
        session.add(user)
        await session.commit()

    # Asosiy menyu tugmalari
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📂 Fayl yuklash")],
            [KeyboardButton(text="🗂 Kategoriyalar")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        f"Salom, {message.from_user.first_name or 'anonim'}! 👋",
        reply_markup=kb
    )