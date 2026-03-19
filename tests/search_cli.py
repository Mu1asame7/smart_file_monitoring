import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from indexer.database import FileDataBase


def main():
    db = FileDataBase()
    while True:
        query = input("\n🔍 Поиск (или 'exit'): ")
        if query.lower() == "exit":
            break
        results = db.search(query)
        for path, filename, category in results:
            print(f"📄 {filename} ({category})")
            print(f"   {path}\n")


if __name__ == "__main__":
    main()
