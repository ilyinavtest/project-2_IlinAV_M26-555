"""Декораторы для базы данных."""

import functools
import time


def handle_db_errors(func):
    """Перехватывать стандартные ошибки БД"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as exc:
            print(f"Ошибка: Таблица или столбец не найдены ({exc}).")
        except ValueError as exc:
            print(f"Ошибка валидации: {exc}")
        except FileNotFoundError as exc:
            print(f"Ошибка: Файл не найден ({exc}).")
        except Exception as exc:  # noqa: BLE001
            print(f"Непредвиденная ошибка: {exc}")

    return wrapper

def confirm_action(action_name: str):
    """Запрашивать у пользователя подтверждение перед опасной операцией."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Замерять время выполнения функции и выводить его в консоль."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result

    return wrapper