"""Движок базы данных: запуск, игровой цикл и парсинг команд."""

import shlex

from prompt_toolkit import prompt

from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata

DB_FILE = "db_meta.json"


def _print_help() -> None:
    """Вывести справочную информацию."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> "
        "<столбец1:тип> <столбец2:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")


def _list_tables(metadata: dict) -> None:
    """Вывести список всех таблиц."""
    if not metadata:
        print("Нет созданных таблиц.")
        return
    for table_name in sorted(metadata.keys()):
        print(f"- {table_name}")


def run() -> None:
    """Запустить основной цикл программы."""
    print("database")
    print()
    _print_help()

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

        if command == "exit":
            print("Выход из программы.")
            break
        elif command == "help":
            _print_help()
        elif command == "list_tables":
            metadata = load_metadata(DB_FILE)
            _list_tables(metadata)
        elif command == "create_table":
            if len(cmd_args) < 2:
                print("Ошибка: Использование: create_table <имя> <колонка:тип> ...")
                continue
            metadata = load_metadata(DB_FILE)
            metadata = create_table(metadata, cmd_args[0], cmd_args[1:])
            save_metadata(DB_FILE, metadata)
        elif command == "drop_table":
            if len(cmd_args) != 1:
                print("Ошибка: Использование: drop_table <имя_таблицы>")
                continue
            metadata = load_metadata(DB_FILE)
            metadata = drop_table(metadata, cmd_args[0])
            save_metadata(DB_FILE, metadata)
        else:
            print(f"Функции {command} нет. Попробуйте снова.")