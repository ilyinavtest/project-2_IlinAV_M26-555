README 
TEST EDUCATIONAL PROJECT

## Управление таблицами

### Доступные команды:
- `create_table <имя> <колонка1:тип> <колонка2:тип> ...` — создать таблицу.
- `list_tables` — показать список всех таблиц.
- `drop_table <имя>` — удалить таблицу.
- `help` — показать справку.
- `exit` — выйти из программы.

### Поддерживаемые типы данных:
`int`, `str`, `bool`.

### Пример использования:

```text
>>> database
***Процесс работы с таблицей***
Функции:
<command> create_table <имя_таблицы> <столбец1:тип> ... - создать таблицу
...
>>>Введите команду: create_table users name:str age:int
Таблица "users" успешно создана со столбцами:
  - ID: int
  - name: str
  - age: int

>>>Введите команду: list_tables
- users

>>>Введите команду: drop_table users
Таблица "users" успешно удалена.

>>>Введите команду: exit
Выход из программы.

[![asciicast](https://asciinema.org/a/GBFJzLf7b3GHsvGP.svg)](https://asciinema.org/a/GBFJzLf7b3GHsvGP)
