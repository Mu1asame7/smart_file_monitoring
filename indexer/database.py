import sqlite3
import os
import json
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FileDataBase:

    def __init__(self, db_path="file_index.db"):

        self.db_path = db_path
        self._init_table()

    def _init_table(self):

        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            sql_query = (
                "CREATE TABLE IF NOT EXISTS files ("
                "id INTEGER PRIMARY KEY,"
                "path TEXT UNIQUE, "
                "filename TEXT, "
                "extension TEXT, "
                "category TEXT, "
                "size INTEGER, "
                "modified_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
                "content_text TEXT, "
                "status TEXT, "
                "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                ")"
            )
            cursor.execute(sql_query)

            sql_query = (
                "CREATE TABLE IF NOT EXISTS file_moves ("
                "move_id  INTEGER PRIMARY KEY,"
                "file_id INTEGER, "
                "old_path TEXT, "
                "new_path TEXT, "
                "moved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
                "FOREIGN KEY (file_id) REFERENCES files(id)"
                ")"
            )
            cursor.execute(sql_query)

            sql_query = (
                "CREATE VIRTUAL TABLE IF NOT EXISTS files_fts "
                "USING fts5(filename, content_text, content=files)"
            )
            cursor.execute(sql_query)

    def add_file(self, path_file: str, category: str, content_text: str = ""):

        filename = os.path.basename(path_file)
        extension = os.path.splitext(filename)[1]
        size_file = os.path.getsize(path_file)
        modified_time = datetime.fromtimestamp(os.path.getmtime(path_file))
        status = "active"
        created_at = datetime.fromtimestamp(os.path.getctime(path_file))
        content_text = self._extract_text(path_file)

        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT id FROM files WHERE path = ?", (path_file,))
            existing = cursor.fetchone()

            if not existing:
                sql_query = """
                INSERT INTO files 
                (path, filename, extension, category, size, modified_time, content_text, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    path_file,
                    filename,
                    extension,
                    category,
                    size_file,
                    modified_time,
                    content_text,
                    status,
                    created_at,
                )
            else:
                sql_query = """
                UPDATE files 
                SET filename=?, extension=?, category=?, size=?, modified_time=?, content_text=?, status=?
                WHERE path=?
                """
                params = (
                    filename,
                    extension,
                    category,
                    size_file,
                    modified_time,
                    content_text,
                    status,
                    path_file,
                )

            cursor.execute(sql_query, params)
            connection.commit()

    def record_move(self, old_path: str, new_path: str):
        print(f"\n📦 RECORD_MOVE START")
        print(f"   old_path: {old_path}")
        print(f"   new_path: {new_path}")
        print(f"   БД: {self.db_path}")
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()

            # Проверяем, существует ли уже новый путь у другого файла
            cursor.execute(
                "SELECT id FROM files WHERE path = ? AND path != ?",
                (new_path, old_path),
            )
            existing = cursor.fetchone()

            if existing:
                print(f"⚠️ Новый путь уже занят файлом id={existing[0]}")
                cursor.execute("DELETE FROM files WHERE id = ?", (existing[0],))
                print(f"✅ Старая запись удалена")

            cursor.execute("SELECT id FROM files WHERE path = ?", (old_path,))
            result = cursor.fetchone()
            if not result:
                return None

            file_id = result[0]

            cursor.execute(
                "INSERT INTO file_moves (file_id, old_path, new_path) VALUES (?, ?, ?)",
                (file_id, old_path, new_path),
            )

            cursor.execute(
                "UPDATE files SET path = ? WHERE id = ?", (new_path, file_id)
            )

            connection.commit()
            return file_id

    def mark_deleted(self, path: str):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE files SET status = 'deleted' WHERE path = ?", (path,)
            )
            connection.commit()

    def is_file_indexed(self, path: str) -> bool:
        """Проверяет, есть ли файл в базе данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM files WHERE path = ?", (path,))
            return cursor.fetchone() is not None

    def _extract_text(self, file_path):

        if not os.path.exists(file_path):
            logger.warning(f"Файл {file_path} не существует")
            return ""

        file_size = os.path.getsize(file_path)

        if file_size > 10 * 1024 * 1024:
            logger.warning(
                f"Файл {file_path} слишком большой ({file_size} bytes). Пропускаем"
            )
            return ""

        ext = os.path.splitext(file_path)[1]

        if not ext == ".txt":
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="cp1251") as file:
                content = file.read()
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {file_path}: {e}")

        return content

    def search(self, query: str):
        print(f"🔍 Поиск запроса: '{query}'")
        print(f"📂 База данных: {self.db_path}")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
            SELECT f.path, f.filename, f.category
            FROM files f
            JOIN files_fts fts ON f.id = fts.rowid
            WHERE files_fts MATCH ?
            ORDER BY rank
        """,
                (query,),
            )
            results = cursor.fetchall()
            print(f"📊 Найдено результатов: {len(results)}")
            return results

    # def recreate_fts(self):
    #     with sqlite3.connect(self.db_path, timeout=10) as conn:
    #         cursor = conn.cursor()

    #         # Удаляем старую виртуальную таблицу
    #         cursor.execute("DROP TABLE IF EXISTS files_fts")

    #         # Создаем заново с явным tokenizer
    #         cursor.execute(
    #             """
    #             CREATE VIRTUAL TABLE files_fts
    #             USING fts5(
    #                 filename,
    #                 content_text,
    #                 tokenize='porter unicode61',
    #                 content=files
    #             )
    #         """
    #         )

    #         # Заполняем данными
    #         cursor.execute(
    #             """
    #             INSERT INTO files_fts(rowid, filename, content_text)
    #             SELECT id, filename, content_text FROM files
    #         """
    #         )

    #         # Принудительно перестраиваем индекс (на всякий случай)
    #         cursor.execute("INSERT INTO files_fts(files_fts) VALUES('rebuild')")

    #         conn.commit()
    #         print("FTS5 таблица пересоздана и индекс построен")
