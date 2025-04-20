import random
import time
from pymongo import MongoClient
import redis
import numpy as np
from collections import defaultdict
from datetime import datetime

# Configuración
MONGO_URI = "mongodb://root:example@mongodb:27017"
REDIS_HOST = "redis"
REDIS_PASSWORD = "yourpassword"

# Conexiones
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.traffic_data
collection = db.events

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# Métricas globales
metrics = {
    'start_time': datetime.now(),
    'total_queries': 0,
    'cache_hits': 0,
    'cache_misses': 0,
    'response_times': [],
    'event_type_counts': defaultdict(int),
    'distribution_metrics': {
        'exponential': {'queries': 0, 'hits': 0, 'response_times': []},
        'normal': {'queries': 0, 'hits': 0, 'response_times': []}
    },
    'location_counts': defaultdict(int)
}

# Distribuciones de llegada
def exponential_arrival(rate):
    while True:
        yield random.expovariate(rate)

def normal_arrival(mean, std_dev):
    while True:
        yield max(0.1, random.normalvariate(mean, std_dev))  # Mínimo 0.1 segundos

def print_metrics():
    total = metrics['cache_hits'] + metrics['cache_misses']
    run_time = (datetime.now() - metrics['start_time']).total_seconds()
    redis_info = redis_client.info('memory')
    print(f"• Uso Redis: {redis_info['used_memory_human']} / {redis_info['maxmemory_human']}")
    
    # Métricas generales
    hit_rate = metrics['cache_hits'] / total if total > 0 else 0
    avg_response = np.mean(metrics['response_times']) if metrics['response_times'] else 0
    qps = total / run_time if run_time > 0 else 0
    
    print("\n=== Métricas del Sistema ===")
    print(f"• Tiempo ejecución: {run_time:.2f} segundos")
    print(f"• Total queries: {metrics['total_queries']}")
    print(f"• Queries/sec: {qps:.2f}")
    print(f"• Cache Hit Rate: {hit_rate:.2%}")
    print(f"• Avg Response Time: {avg_response:.4f}s")
    
    # Métricas por tipo de evento
    print("\n• Distribución por Tipo de Evento:")
    for event_type, count in sorted(metrics['event_type_counts'].items(), key=lambda x: x[1], reverse=True):
        print(f"  - {event_type:<12}: {count:>5} ({count/total:.1%})")
    
    # Métricas por ubicación (top 5)
    print("\n• Top 5 Ubicaciones:")
    for location, count in sorted(metrics['location_counts'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {location:<20}: {count:>5} eventos")
    
    # Métricas por distribución
    print("\n=== Métricas por Distribución ===")
    for dist, data in metrics['distribution_metrics'].items():
        if data['queries'] > 0:
            dist_hit_rate = data['hits'] / data['queries']
            dist_avg_response = np.mean(data['response_times']) if data['response_times'] else 0
            print(f"• {dist.capitalize():<12}:")
            print(f"  - Queries:    {data['queries']:>5}")
            print(f"  - Hit Rate:   {dist_hit_rate:.2%}")
            print(f"  - Avg Time:   {dist_avg_response:.4f}s")
    
    print("="*50)

def generate_traffic(distribution, params):
    if distribution == "exponential":
        arrival_times = exponential_arrival(params['rate'])
    elif distribution == "normal":
        arrival_times = normal_arrival(params['mean'], params['std_dev'])
    
    while True:
        try:
            start_time = time.time()
            delay = next(arrival_times)
            time.sleep(delay)
            
            # Consultar evento aleatorio
            count = collection.count_documents({})
            if count == 0:
                continue
                
            event = collection.find().sort("timestamp", -1).limit(100).skip(random.randint(0, 99)).next()
            
            # Verificar caché
            event_key = f"event:{event['_id']}"
            cached_event = redis_client.get(event_key)
            
            response_time = time.time() - start_time
            
            # Actualizar métricas
            metrics['total_queries'] += 1
            metrics['response_times'].append(response_time)
            metrics['event_type_counts'][event['type']] += 1
            metrics['location_counts'][event['location']] += 1
            metrics['distribution_metrics'][distribution]['queries'] += 1
            metrics['distribution_metrics'][distribution]['response_times'].append(response_time)
            
            if cached_event:
                metrics['cache_hits'] += 1
                metrics['distribution_metrics'][distribution]['hits'] += 1
                print(f"[HIT] Evento {event['_id']} en caché | Tipo: {event['type']} | Loc: {event['location']}")
            else:
                metrics['cache_misses'] += 1
                redis_client.set(event_key, str(event))
                redis_client.expire(event_key, 3600)
                print(f"[MISS] Evento {event['_id']} almacenado | Tipo: {event['type']} | Sev: {event['severity']}")
            
            if metrics['total_queries'] % 50 == 0:
                print_metrics()
                
        except Exception as e:
            print(f"Error en generación de tráfico: {str(e)}")
            time.sleep(5)  # Esperar antes de reintentar

if __name__ == "__main__":
    # Configuración de distribuciones
    distributions = [
        ("exponential", {"rate": 2.0}),  # 2 eventos/segundo (lambda)
        ("normal", {"mean": 0.5, "std_dev": 0.1})  # Media 0.5s, desviación 0.1s
    ]
    
    # Iniciar con la primera distribución
    current_dist = 0
    dist_name, params = distributions[current_dist]
    
    print("=== Iniciando Generador de Tráfico ===")
    print(f"Configuración inicial: {dist_name} con params {params}")
    print("Ctrl+C para detener\n")
    
    try:
        while True:
            print(f"\nCambiando a distribución {dist_name}...")
            generate_traffic(dist_name, params)
            
            # Rotar distribución cada 5 minutos
            time.sleep(300)
            current_dist = (current_dist + 1) % len(distributions)
            dist_name, params = distributions[current_dist]
            
    except KeyboardInterrupt:
        print("\n=== Métricas Finales ===")
        print_metrics()
        print("Deteniendo generador de tráfico...")
