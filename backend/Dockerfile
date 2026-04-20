FROM python:3.12.8-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn whitenoise

COPY . /app/

# Run collectstatic during the build. (Requires a dummy SECRET_KEY if settings expect one)
RUN SECRET_KEY=dummy python manage.py collectstatic --noinput

CMD ["gunicorn", "erp_core.wsgi:application", "--bind", "0.0.0.0:8000"]
