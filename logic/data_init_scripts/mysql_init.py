from util.mysql_connector import MySQLConnector

# Метод выполнения запросов создания таблиц базы данных в MySQL
def mysql_init():
    msql_conn = MySQLConnector()
    # Открываем файл со скриптом создания таблиц
    with open("/app/src/sql/init_mysql.sql") as file:
        sql_query = file.read()
    rows = msql_conn.execute_commit_query(sql_query)
