# Economic Research Platform

Веб-приложение для анализа влияния финансового сектора на экономический рост с использованием данных Всемирного банка и пользовательских датасетов.

## 🚀 Запуск проекта

### 1. Клонируй проект и создай `.env`

```bash
cp .env.example .env
```

### 2. Собери и запусти контейнеры

```bash
docker-compose up --build
```

### 3. Открой Swagger UI

```text
http://localhost:8000/docs
```

## 🧪 Тестирование

```bash
docker-compose exec web bash
pip install pytest
pytest /app/test_main.py -v
```

## 📦 Стек технологий

- FastAPI
- PostgreSQL
- SQLAlchemy
- Pandas + linearmodels
- React + Tailwind (фронтенд)