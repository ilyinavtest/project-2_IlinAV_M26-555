#!/usr/bin/env python3
"""Точка входа базы данных."""

from primitive_db.engine import welcome


def main() -> None:
    """Запустить базу данных."""
    welcome()


if __name__ == "__main__":
    main()