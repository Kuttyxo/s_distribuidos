import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time
import random

# Conexión a MongoDB
client = MongoClient("mongodb://root:example@mongodb:27017")
db = client.traffic_data
collection = db.events

def scrape_waze():
    url = "https://www.waze.com/es-419/live-map/"
    event_types = ['ACCIDENT', 'JAM', 'ROAD_CLOSED', 'HAZARD', 'POLICE', 'CONSTRUCTION']
    locations = [
        "Santiago Centro", "Providencia", "Las Condes", "Ñuñoa",
        "Maipú", "La Florida", "Puente Alto", "San Bernardo"
    ]
    
    try:
        # Simulación de datos
        event = {
            "type": random.choice(event_types),
            "location": random.choice(locations),
            "timestamp": int(time.time() * 1000),
            "severity": random.randint(1, 5),
            "description": f"{random.choice(event_types)} en {random.choice(locations)}"
        }
        
        # Insertar solo si no existe un evento similar reciente
        if not collection.find_one({
            "type": event["type"],
            "location": event["location"],
            "timestamp": {"$gt": int(time.time() * 1000) - 30000}  # 30 segundos
        }):
            collection.insert_one(event)
            print(f"Evento insertado: {event}")
        else:
            print(f"Evento duplicado omitido: {event['type']} en {event['location']}")
            
    except Exception as e:
        print(f"Error al procesar datos: {str(e)}")

def generate_initial_data():
    """Genera datos iniciales para pruebas"""
    print("Generando datos iniciales...")
    for _ in range(100):
        scrape_waze()
        time.sleep(0.1)

if __name__ == "__main__":
    generate_initial_data()
    while True:
        scrape_waze()
        time.sleep(1)
