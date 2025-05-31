FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y gcc python3-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001
CMD ["python", "storage_service.py"]