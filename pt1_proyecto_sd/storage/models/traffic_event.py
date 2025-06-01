from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

class TrafficEventStorage:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.client[os.getenv("MONGO_DB", "traffic_data")]
        self.collection = self.db["traffic_events"]
        
    def get_random_event(self):
        """Obtiene un evento aleatorio de la base de datos"""
        return self.collection.aggregate([{"$sample": {"size": 1}}]).next()
    
    def count_events(self):
        """Cuenta el total de eventos almacenados"""
        return self.collection.count_documents({})
    
    def get_events_by_type(self, event_type, limit=10):
        """Obtiene eventos por tipo"""
        return list(self.collection.find({"event_type": event_type}).limit(limit))
    
    def close_connection(self):
        """Cierra la conexión con MongoDB"""
        self.client.close()