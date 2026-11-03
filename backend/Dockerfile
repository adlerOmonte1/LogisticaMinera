# Imagen del backend para desarrollo y preproduccion (PLAN-02, F0).
# Python 3.12, la misma version del CI (.github/workflows/backend.yml).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Lima

WORKDIR /app

# Motor de reconocimiento provisional (D-12): Tesseract local, sin servicio
# externo. Solo lo usa apps/reconocimiento/motores/tesseract.py.
RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/dev.txt

COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
