import os
import time
import requests
from datetime import datetime
import logging
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WazeScraper:
    def __init__(self):
        self.base_url = "https://www.waze.com/live-map/api/georss"
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://root:example@localhost:27017")
        self.db_name = os.getenv("MONGO_DB", "traffic_data")
        self.interval = int(os.getenv("SCRAPER_INTERVAL_MINUTES", 5))
        self.client = None
        self.db = None
        self.events_collection = None
        self._init_db()
        
    def _init_db(self):
        """Inicializa la conexión con MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.events_collection = self.db["traffic_events"]
            
            # Crear índices
            self.events_collection.create_index([("id", 1)], unique=True)
            self.events_collection.create_index([("location", "2dsphere")])
            
            logger.info("Conexión a MongoDB establecida")
        except PyMongoError as e:
            logger.error(f"Error al conectar con MongoDB: {e}")
            raise

    def get_region_bounding_boxes(self):
        """Bounding boxes para Región Metropolitana"""
        return [
            {"top": -33.35, "bottom": -33.45, "left": -70.9, "right": -70.6},  # Centro
            {"top": -33.35, "bottom": -33.45, "left": -70.6, "right": -70.3},  # Este
            {"top": -33.45, "bottom": -33.55, "left": -70.9, "right": -70.6},  # Sur
            {"top": -33.45, "bottom": -33.55, "left": -70.6, "right": -70.3},  # Sureste
            {"top": -33.35, "bottom": -33.45, "left": -71.2, "right": -70.9},  # Oeste
            {"top": -33.45, "bottom": -33.63, "left": -71.2, "right": -70.9},  # Suroeste
        ]

    def fetch_events(self, bbox):
        """Obtiene eventos de Waze para un bounding box"""
        params = {**bbox, "env": "row", "types": "alerts,traffic"}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        try:
            response = requests.get(self.base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json().get("alerts", [])
        except Exception as e:
            logger.error(f"Error al obtener datos: {e}")
            return []

    def process_event(self, event):
        """Procesa un evento para almacenar en MongoDB"""
        location = event.get("location", {})
        return {
            "id": event.get("uuid"),
            "event_type": event.get("type"),
            "subtype": event.get("subtype"),
            "street": event.get("street"),
            "city": event.get("city"),
            "location": {
                "type": "Point",
                "coordinates": [location.get("x"), location.get("y")]
            },
            "timestamp": datetime.now(),
            "raw_data": event
        }

    def save_events(self, events):
        """Almacena eventos en MongoDB"""
        if not events:
            return
            
        try:
            docs = [self.process_event(e) for e in events]
            result = self.events_collection.insert_many(docs, ordered=False)
            logger.info(f"Insertados {len(result.inserted_ids)} eventos")
        except PyMongoError as e:
            logger.error(f"Error al guardar eventos: {e}")

    def run(self):
        """Ejecuta el scraper en un loop infinito"""
        logger.info(f"Iniciando scraper con intervalo de {self.interval} minutos")
        
        try:
            while True:
                start = time.time()
                total = 0
                
                for bbox in self.get_region_bounding_boxes():
                    events = self.fetch_events(bbox)
                    if events:
                        self.save_events(events)
                        total += len(events)
                        logger.info(f"Procesados {len(events)} eventos")
                    time.sleep(1)
                
                logger.info(f"Ciclo completado. Total eventos: {total}")
                elapsed = time.time() - start
                sleep = max(0, self.interval * 60 - elapsed)
                time.sleep(sleep)
                
        except KeyboardInterrupt:
            logger.info("Scraper detenido por el usuario")
        finally:
            if self.client:
                self.client.close()

if __name__ == "__main__":
    scraper = WazeScraper()
    scraper.run()