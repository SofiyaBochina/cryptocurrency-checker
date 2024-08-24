import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
COINMARKET_TOKEN = os.getenv("COINMARKET_TOKEN")
CHECK_INTERVAL_SEC = int(os.getenv("CHECK_INTERVAL_SEC"))
DATABASE_URL = os.getenv("DATABASE_URL")
