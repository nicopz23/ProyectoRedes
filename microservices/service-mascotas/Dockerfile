FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema y curl para healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de Python
COPY microservices/service-mascotas/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar módulos comunes, dataset y código del servicio
COPY microservices/common ./microservices/common
COPY database/dataset_censo_mascotas.csv ./database/
COPY microservices/service-mascotas/main.py .

ENV PYTHONPATH=/app
ENV PORT=8002

EXPOSE 8002

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8002/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]

