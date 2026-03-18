import os

def get_file_category(path: str) -> str:
    categories = {
    'Изображения': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
    'Документы': ['.pdf', '.docx', '.txt', '.rtf', '.odt', '.doc'],
    'Видео': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
    'Архивы': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'Музыка': ['.mp3', '.wav', '.flac', '.aac'],
    'Исполняемые': ['.exe', '.msi', '.bat', '.sh'],
    'Прочее': []
    }
    extension = os.path.splitext(path)[1].lower()

    for category, extensions in categories.items():
        if extension in extensions:
            return category
        
    return "Прочее"