# exporter/export_to_csv.py

import os
import csv
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:example@mongodb:27017")
DB_NAME = os.getenv("MONGO_DB", "traffic_data")
COLLECTION = "traffic_events"
OUTPUT_PATH = "/data/raw/events.csv"  # Montado desde docker-compose

def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION]

    with open(OUTPUT_PATH, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "event_type", "comuna", "timestamp", "description"])  # encabezado

        for event in collection.find():
            try:
                writer.writerow([
                    event.get("id", ""),
                    event.get("event_type", ""),
                    event.get("city", ""),  # comuna
                    event.get("timestamp", ""),
                    event.get("street", "") or ""
                ])
            except Exception as e:
                print(f"Error writing event: {e}")

    print(f"Exported data to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
