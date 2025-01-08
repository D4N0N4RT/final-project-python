from mysql_init import mysql_init
from pg_init import pg_init
from pg_data_generation import generate_postgres_data


def main():
    # Сначала создаем таблицы в PostgreSQL
    pg_init()
    # Потом создаем таблицы в MySQL
    mysql_init()
    # В конце заполняем таблицы PostgreSQL данными
    generate_postgres_data()


if __name__ == "__main__":
    main()
