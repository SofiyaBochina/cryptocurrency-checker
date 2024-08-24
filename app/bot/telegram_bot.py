import logging

from aiogram import Bot, Dispatcher
from settings.config import BOT_TOKEN
from settings.logger import logger

from .handlers import router

logging.getLogger("aiogram").setLevel(logging.DEBUG)
logging.getLogger("aiogram").handlers = logger.handlers

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def start_bot():
    dp.include_router(router)
    await dp.start_polling(bot)
