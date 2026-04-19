FROM python:3.11-slim

WORKDIR /app

# Instalace systémových závislostí pro PostgreSQL a Python
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Kopie requirements a instalace závislostí
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopie celého projektu
COPY . .

# Sběr statických souborů
RUN python manage.py collectstatic --noinput

# Export proměnných prostředí
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Spuštění aplikace pomocí gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "stock_project.wsgi:application"]
