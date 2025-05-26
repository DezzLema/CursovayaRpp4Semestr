# Базовый образ Python
FROM python:3.10-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование requirements.txt
COPY requirements.txt .

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt

# Установка matplotlib с агрегативным бэкендом
ENV MATPLOTLIBRC=/etc/matplotlib
RUN mkdir -p /etc/matplotlib && \
    echo "backend : Agg" > /etc/matplotlib/matplotlibrc

# Копирование всего проекта
COPY . .

# Сборка статических файлов (если используете)
# RUN python manage.py collectstatic --noinput

# Порт для Django
EXPOSE 8000

# Команда запуска
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "graph_site.wsgi:application"]