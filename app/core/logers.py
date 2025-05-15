import logging

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
console_handler = logging.StreamHandler()

logger.addHandler(file_handler)
logger.addHandler(console_handler)

formatter = logging.Formatter(
    "{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
