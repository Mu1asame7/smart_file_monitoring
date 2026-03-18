# tests/test_classifier.py
import sys
import os

# Добавляем путь к проекту, чтобы импортировать модуль
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.classifier import get_file_category

def test_classifier():
    print("=== Тестирование классификатора ===\n")
    
    test_files = [
        ("cat.jpg", "Изображения"),
        ("document.pdf", "Документы"),
        ("video.mp4", "Видео"),
        ("archive.zip", "Архивы"),
        ("song.mp3", "Музыка"),
        ("setup.exe", "Исполняемые"),
        ("unknown.xyz", "Прочее")
    ]
    
    for file_path, expected in test_files:
        result = get_file_category(file_path)
        status = "✅" if result == expected else "❌"
        print(f"{status} {file_path:20} -> {result} (ожидалось: {expected})")

if __name__ == "__main__":
    test_classifier()