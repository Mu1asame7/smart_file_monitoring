import os
import sys

# Добавляем путь к проекту, чтобы импортировать модуль
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from watchdog.events import FileSystemEventHandler
from core.classifier import get_file_category  # импортируем твой классификатор
from core.organizer import FileOrganizer
from utils.logger import setup_logger
from indexer.database import FileDataBase
from concurrent.futures import ThreadPoolExecutor

# логгер для этого модуля
logger = setup_logger(__name__)


class FileEventHandler(FileSystemEventHandler):

    def __init__(self, organizer):
        self.organizer = organizer
        self.db = FileDataBase()
        logger.info(f"Инициализирован обработчик с папкой {organizer.base_folder}")
        self.executor = ThreadPoolExecutor(max_workers=4)

    def on_created(self, event):

        if event.is_directory:
            logger.debug(f"Пропущена папка: {event.src_path}")
            return

        future = self.executor.submit(self._process_file, event.src_path)

        future.add_done_callback(self._on_task_complete)

    def _process_file(self, path):

        try:
            category = get_file_category(path)
            new_path = self.organizer.organize_file(file_path=path, category=category)
            logger.info(
                f"Файл создан и перемещен: {path} -> {new_path} (категория: {category})"
            )
            self.db.add_file(path_file=new_path, category=category)
        except Exception as e:
            logger.error(f"Ошибка при обработке файла {path}: {e}")

    def _on_task_complete(self, future):

        try:
            result = future.result()
            if result:
                logger.info(f"Задача успешно завершена: {result}")
        except Exception as e:
            logger.error(f"Задача упала с ошибкой: {e}")

    def on_deleted(self, event):
        if event.is_directory:
            logger.debug(f"Удалена папка: {event.src_path}")
            return

        path = event.src_path
        category = get_file_category(path)
        self.db.mark_deleted(path=path)

        logger.info(f"Удален файл: {path} -> Категория: {category}")

    def on_moved(self, event):
        """Вызывается при перемещении файла"""
        # Выведи информацию: откуда и куда переместили
        print(f"🔥🔥🔥 Событие on_moved вызвано для {event.src_path}")
        if event.is_directory:
            return

        src = event.src_path
        dest = event.dest_path
        category = get_file_category(dest)  # можно взять по новому пути
        self.db.record_move(old_path=src, new_path=dest)

        logger.info(f"Перемещен файл: {src} -> {dest} | Категория: {category}")


if __name__ == "__main__":
    import time
    from watchdog.observers import Observer

    # Папка для отслеживания (можно поменять)
    watch_path = r"C:\Users\PC\Downloads"

    organizer = FileOrganizer(r"C:\Users\PC\Downloads\Organized")
    event_handler = FileEventHandler(organizer)
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=False)

    observer.start()
    print(f"Отслеживание папки {watch_path} запущено. Для остановки нажми Ctrl+C")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nНаблюдение остановлено")

    observer.join()
