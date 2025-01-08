import os
import logging
import sys
import psycopg2

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_handler = logging.StreamHandler(sys.stdout)
logger_handler.setLevel(logging.DEBUG)
logger.addHandler(logger_handler)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s')
logger_handler.setFormatter(formatter)

connection = {
    "host": os.getenv("PG_HOST"),
    "port": os.getenv("PG_PORT"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "dbname": os.getenv("PG_DB"),
}


class PostgresConnector:

    def __init__(self):
        self.PG_DB = connection.get("dbname", "default_db")
        self.PG_USER = connection.get("user", "default_user")
        self.PG_PWD = connection.get("password", "default_password")
        self.PG_HOST = connection.get("host", "localhost")
        self.PG_PORT = connection.get("port", 5432)

    # Метод соединения с базой данных
    def connect_cursor(self):
        conn_dwh = psycopg2.connect(dbname=self.PG_DB,
                                    user=self.PG_USER,
                                    password=self.PG_PWD,
                                    host=self.PG_HOST,
                                    port=self.PG_PORT,
                                    )
        self.cursor_dwh = conn_dwh.cursor()
        self.conn_dwh = conn_dwh
        return self.conn_dwh

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
    def execute_commit_query(self, query):
        try:
            cursor = self.connect_cursor().cursor()
            cursor.execute(query)
            # Выполняем коммит после завершения выполнения запросов
            self.conn_dwh.commit()
            logger.debug("Query executed successfully.")
            # Логируем полученный результат выполнения запроса
            if cursor.description:
                rows = cursor.fetchall()
                logger.debug(f"Get new records: {len(rows)}")
                return rows
            return None
        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)
        finally:
            self.close_cursor()
            self.close_connection()
