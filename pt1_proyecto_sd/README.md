# 🛣️ Plataforma de Análisis de Tráfico - Entrega 2

Sistema distribuido para el monitoreo, limpieza, procesamiento y análisis de eventos de tráfico en la Región Metropolitana de Santiago, basado en datos reales extraídos desde Waze.

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Arquitectura](#-arquitectura)
- [Módulos](#-módulos)
- [Despliegue](#-despliegue)
- [Flujo de ejecución](#-flujo-de-ejecución)
- [Visualizaciones](#-visualizaciones)
- [Configuración](#-configuración)
- [Tecnologías](#-tecnologías)
- [Repositorio](#-repositorio)
- [Licencia](#-licencia)

---

## 📌 Descripción

Este proyecto tiene como objetivo proporcionar información procesada y útil a la Unidad de Control de Tránsito (UCT) mediante:

- Recolección automatizada de eventos de tráfico desde Waze
- Limpieza, estandarización y deduplicación de los eventos
- Procesamiento distribuido con Apache Pig sobre Hadoop
- Generación de estadísticas y visualizaciones de patrones de tráfico

---


---

## ⚙️ Módulos

- 📡 Scraper: Extrae eventos desde Waze (ubicación, tipo, hora, comuna, descripción).
- 💾 Storage: Almacena eventos en MongoDB.
- 📤 Exporter: Exporta datos limpios a CSV para Pig.
- 🧼 Filtering: Filtra y normaliza datos con Apache Pig (remove nulls, trims, lowercase, dedup).
- 📊 Processing: Procesa datos para análisis por comuna, tipo, hora, día.
- 📈 Visualización: Genera gráficos con Python a partir de los resultados procesados.

---

## 🚀 Despliegue

Requisitos:

- Docker & Docker Compose
- Python 3.10+ (en host) con matplotlib y pandas

Pasos iniciales:

```bash
docker-compose up -d --build

curl http://localhost:5001/events/count //COMPROBAR QUE EL SCRAPER ESTÁ FUNCIONANDO

docker-compose run --rm exporter //Exportar datos de mongodb a ./pig/data/raw/events.csv

```

##  Flujo de ejecución de procesamiento

Entrar a contenedor pig:
```bash
docker exec -it pig_processor bash
```

1. Filtrado y limpieza de eventos:
```bash
pig -x local filter_clean_events.pig

```
Salida generada: /pig/data/clean/clean_events.csv

2. Procesamiento analítico:
```bash
pig -x local process_events.pig
```
Genera:
/pig/data/results/por_comuna/

/pig/data/results/por_tipo/

/pig/data/results/por_dia/

/pig/data/results/por_comuna_tipo/    ------En el documento "part-r-00000" de cada directorio de encuentran los datos

3. Visualización desde host:
```bash
python analyze_incidents.py
python analyze_comuna_tipo.py
python frecuencia_por_incidente.py
python incidentes_comuna.py
```


## 📊 Visualizaciones
Los scripts proporcionados anteriormente realizan las siguientes gráficas en la carpeta principal:

- 📍 Total de incidentes por comuna

- ⚠️ Frecuencia por tipo de incidente

- 🧱 Incidentes por comuna y tipo (gráfico de barras apiladas)

- 📈 Evolución temporal de incidentes por hora y día (opcional)

Estas visualizaciones permiten identificar patrones geográficos, categorías de eventos más comunes y momentos críticos en la ciudad.

## ⚙️ Configuración
Archivo .env de ejemplo:
```bash
# MongoDB
MONGO_URI=mongodb://root:example@mongodb:27017
MONGO_DB=traffic_data

# Scraper
SCRAPER_INTERVAL_MINUTES=1

```


🧪 Tecnologías
Tecnologías utilizadas:

- 🐍 Python 3.10

- 🗃️ MongoDB 5.0

- 🐷 Apache Pig 0.17.0 (modo local, sobre Hadoop)

- 🐳 Docker & Docker Compose

- 📊 Matplotlib & Pandas (visualización)

- 🐘 Pig Latin para procesamiento distribuido

- 🌐 Flask como backend REST del módulo storage

## 🔗 Repositorio
Repositorio del proyecto (Entrega 2):

📁 https://github.com/Kuttyxo/s_distribuidos   ---> en la rama "rich"

Incluye:

- Código fuente de todos los módulos (scraper, storage, exporter, pig, análisis)

- Scripts para procesamiento con Apache Pig

- Gráficos generados automáticamente

- Dockerfile y docker-compose.yml


