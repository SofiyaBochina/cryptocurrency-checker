import asyncio

from bot.telegram_bot import start_bot
from database.database import start_db
from utils.scheduler import start_scheduler


async def main():
    start_db()
    start_scheduler()
    await asyncio.create_task(start_bot())


if __name__ == "__main__":
    asyncio.run(main())
