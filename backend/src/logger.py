import logging
from logging.handlers import RotatingFileHandler
import os

def init_logger():
    """
    Initialize logger
    :return:
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    if not os.path.exists("log"):
        os.makedirs("log")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s : [%(levelname)s] %(message)s"
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    file_handler = logging.FileHandler("log/pricetracker.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    rotating_file_handler = RotatingFileHandler(
        "log/pricetracker_rotating.log", maxBytes=5 * 1024 * 1024, backupCount=3
    )
    rotating_file_handler.setLevel(logging.ERROR)
    rotating_file_handler.setFormatter(formatter)
    logger.addHandler(rotating_file_handler)
