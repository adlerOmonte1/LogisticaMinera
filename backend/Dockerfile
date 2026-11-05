# Imagen del backend para desarrollo y preproduccion (PLAN-02, F0).
# Python 3.12, la misma version del CI (.github/workflows/backend.yml).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Lima

WORKDIR /app

# Motores de reconocimiento locales (D-12), sin servicio externo: Tesseract,
# como linea base, y el modelo TrOCR entrenado. Solo los usan los adaptadores de
# apps/reconocimiento/motores/.
RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/dev.txt

# Modelo local entrenado: PyTorch para CPU, que es lo que tendra el servidor.
# Con OCR_LOCAL=0 la imagen queda sin estas dependencias y el motor `trocr`
# queda no disponible. Los pesos del modelo no van en la imagen: se provisionan
# con `manage.py obtener_modelo`.
ARG OCR_LOCAL=1
RUN if [ "$OCR_LOCAL" = "1" ]; then \
        pip install --no-cache-dir -r requirements/ocr-local.txt \
            --extra-index-url https://download.pytorch.org/whl/cpu; \
    fi

COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
