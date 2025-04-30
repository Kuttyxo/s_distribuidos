## Configuración Requerida

Antes de ejecutar el sistema, asegúrate de:

1. Crear un archivo `.env` con las siguientes variables:
   - `MONGO_URI`: URI de conexión a MongoDB
   - `SCRAPER_INTERVAL_MINUTES`: Intervalo de scraping en minutos
   - `UNIFORM_CACHE_BYTES`: Tamaño máximo del caché FIFO en bytes
   - `NORMAL_CACHE_BYTES`: Tamaño máximo del caché LFU en bytes

## Health Checks

Puedes verificar el estado de los servicios con:

- Storage: `curl http://localhost:5001/health`
- Cache: `curl http://localhost:5002/health`
- MongoDB: Verifica automáticamente en docker-compose