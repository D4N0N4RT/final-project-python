# Итоговый проект по Python

## Запуск

### Описание сервисов из docker-compose
В docker-compose файле описаны следующие сервисы, необходимые для работы системы:
- **airflow-postgres** - контейнер с СУБД PostgreSQL, необходимый для хранения служебных данных из Airflow.
- **airflow-init** - контейнер, в котором запускается процесс инициализации Airflow.
- **postgres** - контейнер с СУБД PostgreSQL, в которой будут храниться основные данные приложения.
- **mysql** - контейнер с СУБД MySQL, в которой будут храниться основные данные приложения.
- **database-data-init** - контейнер со скриптом на языке Python, который создает необходимые таблицы 
в СУБД MySQL и PostgreSQL и заполняет таблицы PostgreSQL данными.
- **airflow-webserver** - контейнер, в котором запускается вэб-сервер Airflow.
- **airflow-scheduler** - контейнер с шэдулером Airflow, который выполняет описанные DAG'и по расписанию.
### Поднятие сервисов
Чтобы запустить все описанные сервисы, выполните:
```bash
docker compose up
```

---

## Airflow

### Вход в Airflow
Перейдите по адресу: [http://localhost:8080/](http://localhost:8080/).  
Используйте следующие учетные данные для входа:
- **Логин:** `admin`
- **Пароль:** `admin`

### Описание созданных DAG в Airflow

#### 1. **`transefer_postgres_mysql`**
- Периодичность: **ежедневно**.
- Функциональность:
  - Репликация данных из Postgres в MySQL.

#### 2. **`analytical_mart`**
- Функциональность:
  - Построение аналитических витрин на основе данных из MySQL.

---
