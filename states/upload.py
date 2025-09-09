from aiogram.fsm.state import State, StatesGroup

# Fayl yuklash jarayoni uchun steytdar
class UploadStates(StatesGroup):
    waiting_for_file = State()       # Foydalanuvchi fayl yuborishini kutish
    waiting_for_category = State()   # Fayl uchun kategoriya tanlash

# Fayl nomini o‘zgartirish jarayoni uchun steytdar
class RenameStates(StatesGroup):
    waiting_for_new_name = State()   # Foydalanuvchi yangi nom yuborishini kutish
