import os
import shutil
from pathlib import Path
from utils.logger import setup_logger
import time

# Создание логгера
logger = setup_logger(__name__)


class FileOrganizer:

    def __init__(self, base_folder: str):

        self.base_folder = base_folder
        self._create_category_folders()
        logger.info(f"Органайзер инициализирован. Базованя папка: {base_folder}")

    def _create_category_folders(self):

        categories = [
            "Изображения",
            "Документы",
            "Видео",
            "Архивы",
            "Музыка",
            "Исполняемые",
            "Прочее",
        ]

        for category in categories:
            folder_path = os.path.join(self.base_folder, category)
            os.makedirs(folder_path, exist_ok=True)
            logger.debug(f"Создана папка: {category}")

        logger.info(f"Создано {len(categories)} папок")

    def organize_file(
        self, file_path: str, category: str, max_retries=5, delay=0.5
    ) -> str:
        """
        Перемещает файл в соответствующую папку категории

        Args:
            file_path: Путь к исходному файлу
            category: Категория файла (Images, Documents и т.д.)

        Returns:
            str: Новый путь к файлу или None если ошибка
        """

        if not os.path.exists(file_path):
            logger.error(f"Файл не существует: {file_path}")
            return None

        target_folder = os.path.join(self.base_folder, category)
        os.makedirs(target_folder, exist_ok=True)

        filename = os.path.basename(file_path)
        dest_path = os.path.join(target_folder, filename)

        if os.path.exists(dest_path):
            logger.warning(f"Обнаружен дубликат: {dest_path}")
            dest_path = self._handle_puplicate(dest_path)

        for attempt in range(max_retries):
            try:
                shutil.move(file_path, dest_path)
                logger.info(f"Файл перемещен: {file_path} -> {dest_path}")
                return dest_path
            except PermissionError as e:
                if attempt < max_retries:
                    logger.warning(
                        f"Файл занят, попытка{attempt + 1}/{max_retries} через{delay}с"
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        f"Не удалось переместить {file_path} после {max_retries} попыток: {e}"
                    )
                    return None
            except Exception as e:
                logger.error(f"Ошибка при перемещении {file_path}: {e}")
                return None

    def _handle_puplicate(self, dest_path):

        base, ext = os.path.splitext(dest_path)
        counter = 1
        new_path = f"{base}({counter}){ext}"

        while os.path.exists(new_path):
            counter += 1
            new_path = f"{base}({counter}){ext}"

        logger.debug(f"Создано новое имя для дубликата: {new_path}")
        return new_path
