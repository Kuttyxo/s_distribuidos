# Plataforma de Análisis de Tráfico en Región Metropolitana

Sistema distribuido para el monitoreo y análisis de condiciones de tráfico en tiempo real, basado en datos de Waze.

##  Tabla de Contenidos

- [Descripción](#-descripción)
- [Arquitectura](#-arquitectura)
- [Módulos](#-módulos)
- [Despliegue](#-despliegue)
- [Uso](#-uso)
- [Configuración](#-configuración)
- [Métricas](#-métricas)
- [Tecnologías](#-tecnologías)
- [Contribución](#-contribución)
- [Licencia](#-licencia)

##  Descripción

Sistema desarrollado para la **Unidad de Control de Tráfico (UCT)** que permite:

- Extracción automatizada de datos de Waze Live Map
- Almacenamiento eficiente de eventos de tráfico
- Generación de tráfico sintético para pruebas
- Sistema de caché con políticas adaptables
- Visualización de métricas clave


##  Arquitectura

    A[Scraper] -->|Almacena| B[(MongoDB)]
    B -->|Provee datos| C[Generador]
    C -->|Distribuye| D[Cache FIFO/LFU]
    D -->|Provee| E[API Métricas]

##    Módulos

1. Scraper
Función: Extracción de datos de Waze
Frecuencia: Cada 1 minuto (configurable)
Cobertura: 6 sectores de la Región Metropolitana
Salida: Eventos estandarizados en MongoDB

2. Storage
Base de datos: MongoDB 5.0
Índices:
   Geospatial (2dsphere)
   ID único
API REST:
   /events/random - Obtiene evento aleatorio
   /events/count - Cuenta total de eventos

3. Traffic Generator
Distribuciones:
   Uniforme (FIFO): Intervalos 1-3 segundos
   Normal (LFU): Media 2s, σ=0.5

Métricas:
   Tasa de hits
   Latencia promedio

4. Cache System
Política----Uso----Tamaño
FIFO-->Dist.Uniforme-->25KB
LFU---->Dist.Normal---->180KB

## Despliegue
Requisitos
   Docker 20.10+
   Docker Compose 1.29+
   4GB RAM disponibles
   Docker Desktop para mejor experiencia (Requisito principal)


## Uso
PARA CONSTRUIR CONTENEDORES
docker-compose build

PARA LEVANTAR CONTENEDORES
docker-compose up -d

COMANDOS PARA VISUALIZAR
docker compose logs scraper
docker compose logs storage
docker compose logs cache
docker compose logs generator


ENDPOINTS CLAVE
Storage--> /events/random --> GET ---> Evento aleatorio
Cache--> /cache/stats --> GET ---> Estadísticas de caché
Generator--> /metrics --> GET ---> Métricas de generacion


EJEMPLOS DE CONSULTA
curl http://localhost:5001/events/random
curl http://localhost:5001/events/count ---> Cantidad de datos almacenados



## Configuración

Archivo .env:
# MongoDB
MONGO_URI=mongodb://root:example@mongodb:27017
MONGO_DB=traffic_data

# Scraper
SCRAPER_INTERVAL_MINUTES=1

# Cache
UNIFORM_CACHE_BYTES=25600  # 25KB
NORMAL_CACHE_BYTES=184320  # 180KB

# Generator
NORMAL_REUSE_PROBABILITY=0.25
BUFFER_SIZE=12



