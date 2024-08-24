import logging

from aiogram import Bot
from settings.config import BOT_TOKEN
from settings.logger import logger

logging.getLogger("aiogram").setLevel(logging.DEBUG)
logging.getLogger("aiogram").handlers = logger.handlers

bot = Bot(BOT_TOKEN)


async def send_notification(user_id, message):
    try:
        logger.info(f"Sending notify to user {user_id}: {message}")
        await bot.send_message(user_id, message)
    except Exception as e:
        logger.error(
            f'Error while sending notify to user {user_id} with message "{message}": {e}'
        )
