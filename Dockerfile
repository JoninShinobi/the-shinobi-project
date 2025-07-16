FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p staticfiles && python manage.py collectstatic --noinput

EXPOSE 8001

CMD ["gunicorn", "--bind", "0.0.0.0:8001", "shinobi_ops.wsgi:application"]