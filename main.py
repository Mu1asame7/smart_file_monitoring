import time
from watchdog.observers import Observer
from core.organizer import FileOrganizer
from handlers.event_handler import FileEventHandler
from utils.logger import setup_logger
from core.classifier import get_file_category
import os
from indexer.database import FileDataBase

logger = setup_logger(__name__)


def scan_existing_files(folder_path: str, organizer, db):
    """Сканирует существующие файлы и добавляет их в базу"""
    logger.info(f"Начинаю сканирование папки {folder_path}")

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)

            # Пропускаем уже проиндексированные
            if db.is_file_indexed(file_path):
                continue

            # Пропускаем файлы в папке Organized
            if "Organized" in file_path:
                continue

            try:
                # Определяем категорию
                category = get_file_category(file_path)

                new_path = organizer.organize_file(file_path, category)

                # Добавляем в базу
                db.add_file(
                    path_file=new_path,
                    category=category,
                    content_text="",  # позже можно добавить извлечение текста
                )
                logger.info(f"Добавлен файл: {file_path} -> {category}")
            except Exception as e:
                logger.error(f"Ошибка при обработке {file_path}: {e}")

    logger.info("Сканирование завершено")


if __name__ == "__main__":
    watch_path = r"C:\Users\PC\Downloads"
    organized_path = r"C:\Users\PC\Downloads\Organized"

    logger.info(f"Запуск программы. Отслеживаемая папка: {watch_path}")
    logger.info(f"Папка для сортировки: {organized_path}")

    try:
        organizer = FileOrganizer(organized_path)
        db = FileDataBase()
        scan_existing_files(watch_path, organizer, db)
        event_handler = FileEventHandler(organizer)
        observer = Observer()
        observer.schedule(event_handler, watch_path, recursive=True)

        observer.start()
        logger.info("Мониторинг запущен. Для остановки нажми Ctrl+C")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
        observer.stop()
        logger.info("Мониторинг остановлен")

    observer.join()
    logger.info("Программа завершена")
