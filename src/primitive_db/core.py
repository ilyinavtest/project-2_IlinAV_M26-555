"""Основная логика работы с таблицами и данными."""

SUPPORTED_TYPES = {"int", "str", "bool"}


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
            print(f'Ошибка: Неподдерживаемый тип "{col_type}". Доступны: int, str, bool.')
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


def drop_table(metadata: dict, table_name: str) -> dict:
    """Удалить таблицу из metadata."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata