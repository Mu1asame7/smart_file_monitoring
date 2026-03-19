import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import time
from indexer.database import FileDataBase


print("🔄 Перестройка FTS5 индекса...")
print("⚠️ Убедись, что основная программа остановлена!")

time.sleep(3)  # даем время подумать

db = FileDataBase()
db.recreate_fts()
print("✅ Готово!")
