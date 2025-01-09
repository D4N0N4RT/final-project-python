from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from util.mysql_connector import MySQLConnector


# Метод создания витрины
def sale_analisys():
    msql_conn = MySQLConnector()
    with open("/opt/airflow/dags/sql/create_mart_view.sql") as file:
        sql_query = file.read()
    rows = msql_conn.execute_commit_query(sql_query)


# Метод, описывающий ДАГ для создания витрины
with DAG(
        dag_id="analytical_mart",
        start_date=datetime(2023, 12, 1),
        catchup=False,
        tags=["analytical_mart"],
) as dag:
    data_mart_sales = PythonOperator(
        task_id="total_analysis",
        python_callable=sale_analisys,
    )

data_mart_sales
