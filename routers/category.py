from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.category import Category
from models.file import File

router = Router()

# Yangi kategoriya qo‘shish
@router.message(lambda m: m.text and m.text.startswith("/addcat"))
async def add_category(message: Message, session: AsyncSession):
    name = message.text.replace("/addcat", "", 1).strip()

    if not name:
        await message.answer(
            "⚠️ Iltimos, kategoriya nomini yozing.\n\n"
            "Masalan: `/addcat Photos`",
            parse_mode="Markdown"
        )
        return

    try:
        result = await session.execute(
            select(Category).where(Category.name == name)
        )
        existing = result.scalar_one_or_none()

        if existing:
            await message.answer(f"⚠️ Bu kategoriya allaqachon mavjud: {name}")
            return

        cat = Category(name=name)
        session.add(cat)
        await session.commit()

        await message.answer(f"✅ Kategoriya qo‘shildi: {name}")

    except Exception as e:
        await session.rollback()
        await message.answer("❌ Xatolik yuz berdi, keyinroq urinib ko‘ring.")
        raise e

# Kategoriya ichidagi fayllarni ko‘rsatish
@router.message(F.text)
async def show_category_files(message: Message, session: AsyncSession):
    # Kategoriya nomi bo‘yicha DB dan qidirish
    result = await session.execute(
        select(Category).where(Category.name == message.text)
    )
    category = result.scalar_one_or_none()

    if not category:
        return  # boshqa handlerlarga o'tsin

    # Shu kategoriyaga tegishli fayllar
    result = await session.execute(
        select(File).where(File.category_id == category.id)
    )
    files = result.scalars().all()

    if not files:
        await message.answer(f"❌ '{category.name}' kategoriyasida fayl yo‘q.")
        return

    for f in files:
        if f.file_type == "photo":
            await message.answer_photo(f.file_id, caption=f.file_name)
        elif f.file_type == "video":
            await message.answer_video(f.file_id, caption=f.file_name)
        else:
            await message.answer_document(f.file_id, caption=f.file_name)