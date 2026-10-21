import json
from pathlib import Path

DB_FILE = Path("database.json")

SUPPORTED_TYPES = {"int", "str", "bool"}


class TableError(Exception):
    """Базовое исключение для ошибок базы данных."""


class TableAlreadyExistsError(TableError):
    """Таблица уже существует."""


class TableNotFoundError(TableError):
    """Таблица не найдена."""


class InvalidColumnTypeError(TableError):
    """Неподдерживаемый тип данных колонки."""


def _load_db() -> dict:
    """Загрузить базу данных из файла. Вернуть пустой словарь, если файла нет."""
    if not DB_FILE.exists():
        return {}
    with DB_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_db(data: dict) -> None:
    """Сохранить базу данных в файл."""
    with DB_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def create_table(table_name: str, columns_str: list[str]) -> dict:
    """Создать таблицу с указанными колонками.

    columns_str: список строк вида "имя:тип".
    Возвращает созданную структуру таблицы.
    """
    if not table_name:
        raise TableError("Имя таблицы не может быть пустым.")
    if not columns_str:
        raise TableError("Не указаны столбцы таблицы.")

    db = _load_db()

    if table_name in db:
        raise TableAlreadyExistsError(f'Таблица "{table_name}" уже существует.')

    columns = [{"name": "ID", "type": "int"}]
    seen_names = {"ID"}

    for raw in columns_str:
        if ":" not in raw:
            raise TableError(f"Некорректное описание столбца: {raw}")
        name, col_type = raw.split(":", 1)
        name, col_type = name.strip(), col_type.strip()

        if not name or not col_type:
            raise TableError(f"Некорректное описание столбца: {raw}")
        if name in seen_names:
            raise TableError(f'Столбец "{name}" уже определён в таблице.')
        if col_type not in SUPPORTED_TYPES:
            raise InvalidColumnTypeError(
                f'Неподдерживаемый тип "{col_type}". '
                f"Доступны: {', '.join(sorted(SUPPORTED_TYPES))}."
            )

        columns.append({"name": name, "type": col_type})
        seen_names.add(name)

    db[table_name] = {"columns": columns}
    _save_db(db)
    return db[table_name]


def drop_table(table_name: str) -> None:
    """Удалить таблицу по имени."""
    db = _load_db()
    if table_name not in db:
        raise TableNotFoundError(f'Таблица "{table_name}" не существует.')
    del db[table_name]
    _save_db(db)


def list_tables() -> list[str]:
    """Вернуть список имён всех таблиц."""
    return sorted(_load_db().keys())