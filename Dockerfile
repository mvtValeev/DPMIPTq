FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir fastapi uvicorn[standard] sqlalchemy psycopg2-binary httpx python-jose[cryptography] passlib[bcrypt] pandas openpyxl pycountry linearmodels

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]