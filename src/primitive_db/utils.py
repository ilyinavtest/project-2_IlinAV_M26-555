"""Вспомогательные функции для работы с файлами."""

import json
from pathlib import Path

DATA_DIR = Path("data")


def load_metadata(filepath: str) -> dict:
    """Загрузить метаданные из JSON-файла.

    Если файл не найден, возвращает пустой словарь.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    """Сохранить метаданные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_table_data(table_name: str) -> list[dict]:
    """Загрузить данные таблицы из data/<table_name>.json.
    Если файла нет, возвращает пустой список."""
    DATA_DIR.mkdir(exist_ok=True)
    filepath = DATA_DIR / f"{table_name}.json"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if data is not None else []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_table_data(table_name: str, data: list[dict]) -> None:
    """Сохранить данные таблицы в data/<table_name>.json."""
    DATA_DIR.mkdir(exist_ok=True)
    filepath = DATA_DIR / f"{table_name}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)