from util.pg_connector import PostgresConnector

# Метод выполнения запросов создания таблиц базы данных в PostgreSQL
def pg_init():
    pg_conn = PostgresConnector()
    # Открываем файл со скриптом создания таблиц
    with open("/app/src/sql/init_postgres.sql") as file:
        sql_query = file.read()
    rows = pg_conn.execute_commit_query(sql_query)
