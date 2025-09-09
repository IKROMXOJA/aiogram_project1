import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from middlewares.db import DataBaseSession
from routers import start, media, category
from database import init_models

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


async def main():
    # 🔥 Bazada jadvallarni yaratib olish (faqat birinchi marta kerak bo‘ladi)
    await init_models()

    # 🔥 Bot obyektini yaratamiz
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    # 🔥 Dispatcher FSM storage bilan
    dp = Dispatcher(storage=MemoryStorage())

    # 🔥 Middleware ulash (faqat message uchun)
    # dp.message.middleware(DataBaseSession())
    dp.update.middleware(DataBaseSession())

    # 🔥 Routerlarni ulash (tartib bilan)
    dp.include_router(start.router)
    dp.include_router(category.router)
    dp.include_router(media.router)   # oxirida bo‘lsin ⚡️

    # 🔥 Pollingni ishga tushirish
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to‘xtatildi.")
