import logging

logger = logging.getLogger("cryptocurrency-checker")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(levelname)s %(asctime)s - %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)

logger.addHandler(handler)
