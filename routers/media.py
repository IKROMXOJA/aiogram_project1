from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
from aiogram.types import FSInputFile

from models.file import File
from models.user import User
from models.category import Category
from states.upload import UploadStates

router = Router()

# /upload komandasi yoki tugma uchun
@router.message(Command("upload"))
@router.message(F.text == "📂 Fayl yuklash")
async def cmd_upload(message: Message, state: FSMContext):
    await state.set_state(UploadStates.waiting_for_file)
    await message.answer("Iltimos, fayl yuboring 📂")

# Faylni qabul qilish
@router.message(UploadStates.waiting_for_file, F.content_type.in_(["document", "photo", "video"]))
async def handle_file(message: Message, state: FSMContext, session: AsyncSession):
    file_id = None
    file_name = None
    file_type = None

    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name or f"doc_{message.document.file_id}.docx"
        file_type = "document"
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_name = f"photo_{file_id}.jpg"
        file_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name or f"video_{file_id}.mp4"
        file_type = "video"

    # Faylni diskka yuklab olish (masalan, "uploads" papkasiga)
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    file_path = os.path.join(upload_dir, file_name)
    if message.document:
        await message.document.download(destination_file=file_path)
    elif message.photo:
        await message.photo[-1].download(destination_file=file_path)
    elif message.video:
        await message.video.download(destination_file=file_path)

    await state.update_data(file_id=file_id, file_name=file_name, file_type=file_type, file_path=file_path)

    # DB dan kategoriyalarni olish
    result = await session.execute(select(Category))
    categories = result.scalars().all()

    if not categories:
        await message.answer("⚠️ Hali hech qanday kategoriya yo‘q. Avval /addcat bilan qo‘shing.")
        await state.clear()
        return

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=cat.name)] for cat in categories],
        resize_keyboard=True
    )

    await state.set_state(UploadStates.waiting_for_category)
    await message.answer("Kategoriya tanlang:", reply_markup=kb)

# Kategoriya tanlash va DB ga yozish
@router.message(UploadStates.waiting_for_category)
async def handle_category(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    # Foydalanuvchini olish
    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        await message.answer("⚠️ Avval /start buyrug‘ini yuboring.")
        await state.clear()
        return

    # Kategoriya borligini tekshirish
    result = await session.execute(
        select(Category).where(Category.name == message.text)
    )
    category = result.scalar_one_or_none()

    if not category:
        await message.answer("❌ Bunday kategoriya topilmadi. Qayta urinib ko‘ring.")
        return

    # Faylni DB ga saqlash
    new_file = File(
        user_id=user.id,
        file_id=data["file_id"],
        file_name=data["file_name"],
        file_type=data["file_type"],
        category_id=category.id,
        file_path=data["file_path"]  # Fayl yo'lini saqlash
    )
    session.add(new_file)
    await session.commit()

    await state.clear()
    await message.answer(
        f"✅ Fayl saqlandi! Kategoriya: {category.name}",
        reply_markup=ReplyKeyboardRemove()
    )