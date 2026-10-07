# Dockerfile.worker
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Comando de entrada: ejecutar el script del worker directamente
CMD ["python", "worker.py"]