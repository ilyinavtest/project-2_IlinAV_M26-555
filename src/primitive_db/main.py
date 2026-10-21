#!/usr/bin/env python3
"""Точка входа базы данных."""

from primitive_db.engine import run


def main() -> None:
    """Запустить базу данных."""
    run()


if __name__ == "__main__":
    main()