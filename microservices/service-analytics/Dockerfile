FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema, curl y OpenJDK para soporte de Apache Spark
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

COPY microservices/service-analytics/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar módulos comunes, dataset y código fuente del servicio
COPY microservices/common ./microservices/common
COPY database/dataset_censo_mascotas.csv ./database/
COPY microservices/service-analytics/analytics_engine.py .
COPY microservices/service-analytics/main.py .

ENV PYTHONPATH=/app
ENV PORT=8003
ENV JAVA_HOME=/usr/lib/jvm/default-java

EXPOSE 8003

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8003/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]

