import mysql.connector
import os
import sys
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_handler = logging.StreamHandler(sys.stdout)
logger_handler.setLevel(logging.DEBUG)
logger.addHandler(logger_handler)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s')
logger_handler.setFormatter(formatter)

connection = {
    "host": os.getenv("MYSQL_HOST"),
    "port": os.getenv("MYSQL_PORT"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "dbname": os.getenv("MYSQL_DB")
}


class MySQLConnector:

    def __init__(self):
        self.MYSQL_DB = connection.get("dbname", "default_db")
        self.MYSQL_USER = connection.get("user", "default_user")
        self.MYSQL_PWD = connection.get("password", "default_password")
        self.MYSQL_HOST = connection.get("host", "localhost")
        self.MYSQL_PORT = connection.get("port", 3306)

    # Метод соединения с базой данных
    def connect_cursor(self):
        conn_dwh = mysql.connector.connect(database=self.MYSQL_DB,
                                           user=self.MYSQL_USER,
                                           password=self.MYSQL_PWD,
                                           host=self.MYSQL_HOST,
                                           port=self.MYSQL_PORT
                                           )
        self.cursor_dwh = conn_dwh.cursor()
        self.conn_dwh = conn_dwh
        return self.cursor_dwh

    # Метод закрытия курсора
    def close_cursor(self):
        if hasattr(self, 'cursor_dwh'):
            self.cursor_dwh.close()
        return True

    # Метод закрытия соединения
    def close_connection(self):
        if hasattr(self, 'conn_dwh'):
            self.conn_dwh.close()

    # Выполнения запроса из файла
    def get_query(self, file):
        current_path = os.path.dirname(os.path.abspath(__file__))
        with open(current_path + file, 'r') as file:
            sql_query = file.read()
        return sql_query

    # Метод выполнения запроса
    def execute_custom_query(self, query):
        try:
            cursor = self.connect_cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            logger.debug(f"Get new records: {len(rows)}")
            return rows
        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)
        finally:
            self.close_cursor()
            self.close_connection()

    # Метод выполнения запроса с последующим коммитом
    def execute_commit_query(self, query, params=None):
        try:
            cursor = self.connect_cursor()

            if params:
                # Выполняем запрос с параметрами если они есть
                cursor.executemany(query, params)
            else:
                # Выполняем запрос(ы)
                for result in cursor.execute(query, multi=True):
                    logger.debug(f"Running query: {result.statement}")

                    # Логируем полученный результат выполнения запроса
                    if result.with_rows:
                        rows = result.fetchall()
                        logger.debug(f"Rows fetched: {rows}")

            # Выполняем коммит после завершения выполнения запросов
            self.conn_dwh.commit()
            logger.debug("All queries executed and committed successfully.")
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
        finally:
            self.close_cursor()
            self.close_connection()
