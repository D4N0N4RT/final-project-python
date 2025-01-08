import random
from datetime import datetime, timedelta
import logging
import os

from faker import Faker
from faker_commerce import Provider as CommerceProvider
from psycopg2.extensions import cursor
from psycopg2 import OperationalError, DatabaseError
from util.pg_connector import PostgresConnector

faker = Faker()
faker.add_provider(CommerceProvider)

# Инициализация переменных конфигурации
num_users = int(os.getenv('DATAGEN_NUM_USERS', 5000))
num_products = int(os.getenv('DATAGEN_NUM_PRODUCTS', 500))
num_orders = int(os.getenv('DATAGEN_NUM_ORDERS', 10000))
num_order_details = int(os.getenv('DATAGEN_NUM_ORDER_DETAILS', 40000))
num_product_categories = int(os.getenv('DATAGEN_NUM_CATEGORIES', 40000))
user_ids = []
product_ids = []
order_ids = []
category_ids = []

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Метод проверки таблицы на наличие в ней записей
def table_is_empty(cur, table_name):
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cur.fetchone()[0]
    return count == 0


# Метод генерации пользователей
def generate_users(cur: cursor) -> None:
    if not table_is_empty(cur, 'users'):
        logger.info(f"Table users already contains data. Skipping...")
        return

    for _ in range(num_users):
        # Генерируем основную информацию
        first_name = faker.first_name()
        last_name = faker.last_name()

        email = faker.email()
        phone = faker.phone_number()

        registration_date = faker.date_time_between(start_date='-1y', end_date='now')
        loyalty_status = random.choice(["Gold", "Silver", "Bronze"])

        # Выполняем запрос вставки строки в таблицу
        cur.execute(
            "INSERT INTO users (first_name, last_name, email, phone, registration_date, loyalty_status) "
            "VALUES (%s, %s, %s, %s, %s, %s) RETURNING user_id",
            (first_name, last_name, email, phone, registration_date, loyalty_status)
        )
        user_id = cur.fetchone()[0]
        user_ids.append(user_id)


# Метод генерации категорий продуктов
def generate_product_categories(cur: cursor) -> None:
    # Список заранее определенных категорий
    predefined_categories = ["Electronics", "Clothing", "Books", "Home", "Toys", "Sport", "Cars", "Beauty", "Health", "Food"]

    if not table_is_empty(cur, 'product_categories'):
        logger.info(f"Table product_categories already contains data. Skipping...")
        return

    # Вставляем заранее определенные категории
    for category in predefined_categories:
        cur.execute(
            "INSERT INTO product_categories (name, parent_category_id) VALUES (%s, %s) RETURNING category_id",
            (category, None)
        )
        category_id = cur.fetchone()[0]
        category_ids.append(category_id)

    # Генерируем остальные категории
    for _ in range(num_product_categories):
        name = faker.words(nb=1)

        # Определяем, будет ли у категории родительская
        parent_category_id = random.choice(category_ids) if category_ids and random.choice \
            ([True, False]) else None

        cur.execute(
            "INSERT INTO product_categories (name, parent_category_id) VALUES (%s, %s) RETURNING category_id",
            (name, parent_category_id)
        )
        category_id = cur.fetchone()[0]
        category_ids.append(category_id)


def generate_products(cur: cursor) -> None:
    if not table_is_empty(cur, 'products'):
        logger.info(f"Table products already contains data. Skipping...")
        return

    for _ in range(num_products):
        # Генерируем основную информацию
        name = faker.ecommerce_name()
        description = faker.paragraph(nb_sentences=2)

        category_id = random.choice(category_ids)
        price = round(random.uniform(10.0, 100.0), 2)

        stock_quantity = random.randint(1, 100)
        creation_date = datetime.now() - timedelta(days=random.randint(1, 365))

        cur.execute(
            "INSERT INTO products (name, description, category_id, price, stock_quantity, creation_date) "
            "VALUES (%s, %s, %s, %s, %s, %s) RETURNING product_id",
            (name, description, category_id, price, stock_quantity, creation_date)
        )
        product_id = cur.fetchone()[0]
        product_ids.append(product_id)


def generate_orders(cur: cursor) -> None:
    if not table_is_empty(cur, 'orders'):
        logger.info(f"Table orders already contains data. Skipping...")
        return

    for _ in range(num_orders):
        # Генерируем основную информацию о заказе
        user_id = random.choice(user_ids)
        order_date = faker.date_time_between(start_date='-1y', end_date='now')

        total_amount = round(random.uniform(50.0, 500.0), 2)
        status = random.choice(["Pending", "Completed"])
        delivery_date = order_date + timedelta(days=random.randint(1, 10))

        cur.execute(
            "INSERT INTO orders (user_id, order_date, total_amount, status, delivery_date) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING order_id",
            (user_id, order_date, total_amount, status, delivery_date)
        )
        order_id = cur.fetchone()[0]
        order_ids.append(order_id)


def generate_order_details(cur: cursor) -> None:
    if not table_is_empty(cur, 'order_details'):
        logger.info(f"Table order_details already contains data. Skipping...")
        return

    for _ in range(num_order_details):
        # Генерируем основную информацию
        order_id = random.choice(order_ids)
        product_id = random.choice(product_ids)

        quantity = random.randint(1, 10)
        price_per_unit = round(random.uniform(10.0, 100.0), 2)
        total_price = round(price_per_unit * quantity, 2)

        cur.execute(
            "INSERT INTO order_details (order_id, product_id, quantity, price_per_unit, total_price) "
            "VALUES (%s, %s, %s, %s, %s)",
            (order_id, product_id, quantity, price_per_unit, total_price)
        )


def generate_data_for_tables(db_connector: PostgresConnector) -> None:

    with db_connector.connect_cursor() as conn, conn.cursor() as cur:
        try:
            # Последовательно вызываем методы генерации данных для каждой из таблиц
            generate_users(cur)

            generate_product_categories(cur)

            generate_products(cur)

            generate_orders(cur)

            generate_order_details(cur)

            # Выполняем коммит после успешной генерации всех данных
            conn.commit()
            logger.info("Session committed!")
        except (OperationalError, DatabaseError) as e:
            logger.info(f"Error generating data: {e}")


def generate_postgres_data():
    pg_connector = PostgresConnector()

    generate_data_for_tables(pg_connector)

