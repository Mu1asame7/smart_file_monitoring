import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logger(name=__name__, log_to_console=True):

    # Создание папки для логов
    base_folder = r"C:\Users\PC\Downloads\Organized"
    folder_path = os.path.join(base_folder, "logs")
    os.makedirs(folder_path, exist_ok=True)

    # Путь к файлу лога
    log_file = os.path.join(folder_path, "app.log")

    # Создание форматтера
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Создание логгера
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Настройка файлового handler с ротацией
    file_handler = RotatingFileHandler(
        filename=log_file,
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    # Настройка консольного хендлера
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

    return logger
