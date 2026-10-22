"""Движок базы данных: запуск, игровой цикл и парсинг команд."""

import shlex
from typing import Any

from prettytable import PrettyTable
from prompt_toolkit import prompt

from primitive_db.core import create_table, delete, drop_table, insert, select, update
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

DB_FILE = "db_meta.json"


def _print_help() -> None:
    """Вывести справочную информацию."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя> "
        "<столбец1:тип> <столбец2:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя> - удалить таблицу")
    print(
        "<command> insert into <имя> values (<значение1>, <значение2>, ...) "
        "- добавить запись"
    )
    print(
        "<command> select from <имя> where <столбец> = <значение> "
        "- прочитать записи"
    )
    print("<command> select from <имя> - прочитать все записи")
    print(
        "<command> update <имя> set <столбец> = <значение> "
        "where <столбец> = <значение> "
        "- обновить запись"
    )
    print(
        "<command> delete from <имя> where <столбец> = <значение> "
        "- удалить запись"
    )
    print("<command> info <имя> - вывести информацию о таблице")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")


def _list_tables(metadata: dict) -> None:
    """Вывести список всех таблиц."""
    if not metadata:
        print("Нет созданных таблиц.")
        return
    for table_name in sorted(metadata.keys()):
        print(f"- {table_name}")


def _parse_value(val: str) -> Any:
    """Преобразовать строковое значение в Python-объект."""
    val = val.strip()
    # Убираем кавычки, если они есть
    if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
    ):
        return val[1:-1]

    # Пытаемся определить базовые типы
    if val.lower() == "true":
        return True
    if val.lower() == "false":
        return False
    if val.lower() == "none":
        return None

    try:
        return int(val)
    except ValueError:
        return val


def _parse_condition(cond_str: str) -> dict:
    """Разобрать строку вида 'age = 28' в словарь {'age': 28}."""
    # Разделяем по первому знаку '='
    if "=" not in cond_str:
        raise ValueError(f"Некорректное условие: {cond_str}")

    col, val = cond_str.split("=", 1)
    return {col.strip(): _parse_value(val)}


def _display_table(table_name: str, data: list[dict], metadata: dict) -> None:
    """Вывести данные таблицы через PrettyTable."""
    if not data:
        print(f'Таблица "{table_name}" пуста.')
        return

    # Берем колонки из метаданных, чтобы сохранить правильный порядок
    columns = [col["name"] for col in metadata[table_name]["columns"]]

    table = PrettyTable()
    table.field_names = columns

    for row in data:
        table.add_row([row.get(col, "") for col in columns])

    print(table)


def run() -> None:
    """Запустить основной цикл программы."""
    print("database")
    print()
    _print_help()
    cache_result = create_cacher()

    while True:
        try:
            user_input = prompt("\n>>>Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВыход.")
            break

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError as exc:
            print(f"Ошибка парсинга: {exc}")
            continue

        if not args:
            continue

        command = args[0].lower()
        cmd_args = args[1:]

        try:
            if command == "exit":
                print("Выход из программы.")
                break
            elif command == "help":
                _print_help()
            elif command == "list_tables":
                metadata = load_metadata(DB_FILE)
                _list_tables(metadata)
            elif command == "info":
                if len(cmd_args) != 1:
                    print("Ошибка: Использование: info <имя_таблицы>")
                    continue
                metadata = load_metadata(DB_FILE)
                t_name = cmd_args[0]
                if t_name not in metadata:
                    print(f'Ошибка: Таблица "{t_name}" не существует.')
                    continue
                data = load_table_data(t_name)
                cols = ", ".join(
                    f"{c['name']}:{c['type']}" for c in metadata[t_name]["columns"]
                )
                print(f"Таблица: {t_name}")
                print(f"Столбцы: {cols}")
                print(f"Количество записей: {len(data)}")

            elif command == "create_table":
                if len(cmd_args) < 2:
                    print("Ошибка: Использование: create_table <имя> <колонка:тип> ...")
                    continue
                metadata = load_metadata(DB_FILE)
                metadata = create_table(metadata, cmd_args[0], cmd_args[1:])
                save_metadata(DB_FILE, metadata)
                cache_result = create_cacher()
            elif command == "drop_table":
                if len(cmd_args) != 1:
                    print("Ошибка: Использование: drop_table <имя_таблицы>")
                    continue
                metadata = load_metadata(DB_FILE)
                new_metadata = drop_table(metadata, cmd_args[0])
                if new_metadata is not None:
                    save_metadata(DB_FILE, metadata)
                    cache_result = create_cacher()

            # --- CRUD операции ---
            elif command == "insert":
                # insert into users values ("Sergei", 28, true)
                if (
                        len(cmd_args) < 4
                        or cmd_args[0] != "into"
                        or cmd_args[2] != "values"
                ):
                    print("Ошибка: Использование: "
                          "insert into <имя> values (<зн1>, <зн2>...)"
                    )
                    continue

                t_name = cmd_args[1]
                # Собираем всё, что после "values"
                values_str = " ".join(cmd_args[3:])
                # Убираем внешние скобки
                if not (values_str.startswith("(") and values_str.endswith(")")):
                    print(
                        "Ошибка: Значения должны быть в скобках "
                        "(значение1, значение2)"
                    )
                    continue

                values_str = values_str[1:-1]
                # Простой сплит по запятой
                values = [v.strip() for v in values_str.split(",")]

                metadata = load_metadata(DB_FILE)
                table_data = load_table_data(t_name)

                new_data = insert(metadata, table_data, t_name, values)
                if new_data is not None:
                    save_table_data(t_name, new_data)
                    cache_result = create_cacher()

            elif command == "select":
                if len(cmd_args) < 2 or cmd_args[0] != "from":
                    print("Ошибка: Использование: select from <имя> [where ...]")
                    continue

                t_name = cmd_args[1]
                where_clause = None
                where_key = "all"

                if len(cmd_args) > 2:
                    if cmd_args[2] != "where":
                        print("Ошибка: Ожидалось ключевое слово 'where'")
                        continue
                    where_str = " ".join(cmd_args[3:])
                    where_clause = _parse_condition(where_str)
                    where_key = str(where_clause)

                metadata = load_metadata(DB_FILE)
                if t_name not in metadata:
                    print(f'Ошибка: Таблица "{t_name}" не существует.')
                    continue

                cache_key = f"select_{t_name}_{where_key}"

                def fetch_data():
                    table_data = load_table_data(t_name)
                    return select(table_data, where_clause)

                filtered_data = cache_result(cache_key, fetch_data)
                _display_table(t_name, filtered_data, metadata)

            elif command == "update":
                # update users set age = 29 where name = "Sergei"
                if len(cmd_args) < 6 or cmd_args[1] != "set":
                    print(
                        "Ошибка: Использование: update <имя> "
                        "set <столбец> = <зн> where <столбец> = <зн>"
                    )
                    continue

                t_name = cmd_args[0]

                # Находим where
                try:
                    where_idx = cmd_args.index("where")
                except ValueError:
                    print("Ошибка: Отсутствует ключевое слово 'where'")
                    continue

                set_str = " ".join(cmd_args[2:where_idx])
                where_str = " ".join(cmd_args[where_idx + 1:])

                set_clause = _parse_condition(set_str)
                where_clause = _parse_condition(where_str)

                metadata = load_metadata(DB_FILE)
                if t_name not in metadata:
                    print(f'Ошибка: Таблица "{t_name}" не существует.')
                    continue

                table_data = load_table_data(t_name)
                new_data = update(table_data, set_clause, where_clause)
                if new_data is not None:
                    save_table_data(t_name, new_data)
                    cache_result = create_cacher()

            elif command == "delete":
                # delete from users where ID = 1
                if len(cmd_args) < 4 or cmd_args[0] != "from" or cmd_args[2] != "where":
                    print(
                        "Ошибка: Использование: delete "
                        "from <имя> where <столбец> = <зн>"
                    )
                    continue

                t_name = cmd_args[1]
                where_str = " ".join(cmd_args[3:])
                where_clause = _parse_condition(where_str)

                metadata = load_metadata(DB_FILE)
                if t_name not in metadata:
                    print(f'Ошибка: Таблица "{t_name}" не существует.')
                    continue

                table_data = load_table_data(t_name)
                new_data = delete(table_data, where_clause)
                if new_data is not None:
                    save_table_data(t_name, new_data)
                    cache_result = create_cacher()

            else:
                print(f"Функции {command} нет. Попробуйте снова.")

        except Exception as exc:  # noqa: BLE001
            print(f"Некорректное значение или ошибка: {exc}. Попробуйте снова.")


def create_cacher():
    """Создать функцию кэширования (замыкание)"""
    cache = {}

    def cache_result(key: str, value_func):
        """Вернуть значение из кэша или вычислить его и сохранить"""
        if key in cache:
            print(f"[Кэш] Использованы данные по ключу: {key}")
            return cache[key]

        result = value_func()
        cache[key] = result
        print(f"[Кэш] Данные сохранены по ключу: {key}")
        return result

    return cache_result