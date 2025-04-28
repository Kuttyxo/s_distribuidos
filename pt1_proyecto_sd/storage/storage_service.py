from flask import Flask, jsonify
from models.traffic_event import TrafficEventStorage
import logging
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
storage = TrafficEventStorage()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/events/random', methods=['GET'])
def random_event():
    try:
        event = storage.get_random_event()
        # Eliminar _id para evitar problemas de serialización
        event.pop('_id', None)
        return jsonify(event)
    except Exception as e:
        logger.error(f"Error getting random event: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/events/count', methods=['GET'])
def event_count():
    try:
        count = storage.count_events()
        return jsonify({"count": count})
    except Exception as e:
        logger.error(f"Error counting events: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/events/type/<event_type>', methods=['GET'])
def events_by_type(event_type):
    try:
        events = storage.get_events_by_type(event_type)
        for event in events:
            event.pop('_id', None)
        return jsonify(events)
    except Exception as e:
        logger.error(f"Error getting events by type: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)