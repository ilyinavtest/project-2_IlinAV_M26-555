"""Основная логика работы с таблицами и данными."""
from typing import Any

from primitive_db.decorators import confirm_action, handle_db_errors, log_time

SUPPORTED_TYPES = {"int", "str", "bool"}


@handle_db_errors
def create_table(
        metadata: dict,
        table_name: str,
        columns: list[str]
) -> dict:
    """Создать таблицу в metadata.

    columns: список строк вида "имя:тип".
    Автоматически добавляет ID:int в начало.
    """
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    parsed_columns = [{"name": "ID", "type": "int"}]
    seen_names = {"ID"}

    for col_str in columns:
        if ":" not in col_str:
            print(f"Некорректное значение: {col_str}. Попробуйте снова.")
            return metadata

        name, col_type = col_str.split(":", 1)
        if col_type not in SUPPORTED_TYPES:
            print(f'Ошибка: Неподдерживаемый тип "{col_type}". '
                  f'Доступны: int, str, bool.'
            )
            return metadata
        if name in seen_names:
            print(f'Ошибка: Столбец "{name}" уже существует.')
            return metadata

        parsed_columns.append({"name": name, "type": col_type})
        seen_names.add(name)

    metadata[table_name] = {"columns": parsed_columns}
    print(f'Таблица "{table_name}" успешно создана со столбцами:')
    for col in parsed_columns:
        print(f"  - {col['name']}: {col['type']}")

    return metadata


@confirm_action("удаление таблицы")
@handle_db_errors
def drop_table(metadata: dict, table_name: str) -> dict:
    """Удалить таблицу из metadata."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def _convert_value(value: str, col_type: str) -> Any:
    """Конвертировать строковое значение в нужный тип."""
    if col_type == "int":
        return int(value)
    if col_type == "bool":
        if value.lower() in ("true", "1", "yes"):
            return True
        if value.lower() in ("false", "0", "no"):
            return False
        raise ValueError(f"Некорректное значение для bool: {value}")
    return str(value)


@handle_db_errors
@log_time
def insert(
        metadata: dict,
        table_data: list[dict],
        table_name: str,
        values: list[str]
) -> list[dict]:
    """Вставить новую запись в таблицу и вернуть обновленные данные."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data

    columns = metadata[table_name]["columns"]
    data_columns = columns[1:]  # Пропускаем ID

    if len(values) != len(data_columns):
        print(
            f"Ошибка: Ожидалось {len(data_columns)} значений, "
            f"получено {len(values)}."
        )
        return table_data

    try:
        # Генерируем новый ID
        new_id = max((row["ID"] for row in table_data), default=0) + 1
        row = {"ID": new_id}

        for col, val in zip(data_columns, values):
            row[col["name"]] = _convert_value(val, col["type"])

    except ValueError as exc:
        print(f"Ошибка валидации: {exc}")
        return table_data

    table_data.append(row)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


@log_time
@handle_db_errors
def select(table_data: list[dict], where_clause: dict | None = None) -> list[dict]:
    """Прочитать записи с опциональной фильтрацией."""
    if not where_clause:
        return table_data

    result = []
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            result.append(row)
    return result


@handle_db_errors
def update(
        table_data: list[dict],
        set_clause: dict,
        where_clause: dict,
) -> list[dict]:
    """Обновить записи по условию."""
    updated_count = 0
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            for col, val in set_clause.items():
                row[col] = val
            updated_count += 1

    if updated_count == 0:
        print("Ошибка: Записи, подходящие под условие, не найдены.")
    else:
        print(f"Успешно обновлено записей: {updated_count}.")

    return table_data


@confirm_action("удаление записей")
@handle_db_errors
def delete(table_data: list[dict], where_clause: dict) -> list[dict]:
    """Удалить записи по условию."""
    initial_len = len(table_data)
    new_data = [
        row for row in table_data
        if not all(row.get(k) == v for k, v in where_clause.items())
    ]

    deleted_count = initial_len - len(new_data)
    if deleted_count == 0:
        print("Ошибка: Записи, подходящие под условие, не найдены.")
    else:
        print(f"Успешно удалено записей: {deleted_count}.")

    return new_data