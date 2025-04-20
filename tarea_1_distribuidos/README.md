# Sistema de Análisis de Tráfico - Entregable 1

## Descripción
Sistema distribuido para el monitoreo de tráfico en la Región Metropolitana, compuesto por:
- Scraper: Extrae datos de Waze y los almacena en MongoDB
- Generador de tráfico: Simula consultas con diferentes distribuciones de llegada
- Sistema de caché: Utiliza Redis para almacenar consultas frecuentes

## Requisitos
- Docker
- Docker Compose

## Instalación
1. Clonar el repositorio
2. Ejecutar:
```bash
docker-compose up --build
