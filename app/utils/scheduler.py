import asyncio
import logging

from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from bot.notify import send_notification
from database.queries import get_all_subscriptions, get_all_symbols
from settings.config import CHECK_INTERVAL_SEC, COINMARKET_TOKEN
from settings.logger import logger

scheduler = AsyncIOScheduler()
logging.getLogger("apscheduler").setLevel(logging.DEBUG)
logging.getLogger("apscheduler").handlers = logger.handlers


async def get_currencies(session, symbol):
    logger.info(f"get_currencies with symbols: {symbol}")
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {"X-CMC_PRO_API_KEY": COINMARKET_TOKEN}
    params = {"symbol": symbol, "convert": "USD"}

    async with session.get(url, headers=headers, params=params) as response:
        if response.status == 200:
            data = await response.json()
            return data
        else:
            logger.error(
                f"{response.status} Error in API request: {await response.text()}"
            )
            return {}


async def check_prices(currencies, subscriptions):
    logger.info("check_prices")
    for row in subscriptions:
        data = currencies["data"].get(row.symbol)
        if data:
            price = data["quote"]["USD"]["price"]
            logger.info(
                f"subscripton {row.id}: {row.user_id}, {row.symbol}, {row.min_threshold}, {row.max_threshold}; price: {price}"
            )
            if price:
                if price > row.max_threshold:
                    await asyncio.create_task(
                        send_notification(
                            row.user_id,
                            f"Цена {row.symbol} поднялась выше максимального порога {row.max_threshold}. Текущая цена: {price}",
                        )
                    )
                if price < row.min_threshold:
                    await asyncio.create_task(
                        send_notification(
                            row.user_id,
                            f"Цена {row.symbol} упала ниже минимального порога {row.min_threshold}. Текущая цена: {price}",
                        )
                    )


async def fetch_subscriptions():
    logger.info(f"fetch_subscriptions")
    symbols = ",".join(get_all_symbols())
    subscriptions = get_all_subscriptions()
    if subscriptions:
        async with ClientSession() as session:
            currencies = await get_currencies(session, symbols)
        if currencies:
            await check_prices(currencies, subscriptions)
    else:
        logger.info("No active subscriptions")


def start_scheduler():
    scheduler.add_job(fetch_subscriptions, IntervalTrigger(seconds=CHECK_INTERVAL_SEC))
    scheduler.start()
