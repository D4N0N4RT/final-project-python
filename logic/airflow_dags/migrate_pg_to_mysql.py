from datetime import datetime
import yaml

from airflow import DAG
from airflow.operators.python import PythonOperator

from util.pg_connector import PostgresConnector
from util.mysql_connector import MySQLConnector


# Метод чтения данных из таблицы Postgres
def pg_fetch_table(table_name):
    sql_query = f"SELECT * FROM {table_name}"
    pg_conn = PostgresConnector()
    rows = pg_conn.execute_custom_query(sql_query)
    return rows


# Метод вставки данных в MySQL
def mysql_insert_data(table_to_insert, rows):
    placeholders = ', '.join(['%s'] * len(rows[0]))  # One placeholder for each column
    sql_query = f"REPLACE INTO `{table_to_insert}` VALUES ({placeholders})"
    msql_conn = MySQLConnector()
    msql_conn.execute_commit_query(sql_query, rows)


# Метод репликации заданной таблицы
def replicate_table(table):
    fetch_result = pg_fetch_table(table)
    mysql_insert_data(table_to_insert=table,
                      rows=fetch_result)


# Метод описывающий ДАГ репликации всех таблиц из Postgres в MySQL
with DAG(
    dag_id="transfer_postgres_mysql",
    start_date=datetime(2024, 12, 1),
    catchup=False,
    tags=["replication"],
) as dag:

    tables_to_replicate = ["product_categories", "users", "products", "orders", "order_details"]
    # Проходим циклом по всем таблицам
    previous_task = None
    for db_table in tables_to_replicate:
        current_task = PythonOperator(
            task_id=f"replicate_{db_table}",
            python_callable=replicate_table,
            op_args=[db_table]
        )

        # Если предыдущая репликация завершилась, переходим к следующей
        if previous_task:
            previous_task >> current_task
        previous_task = current_task
