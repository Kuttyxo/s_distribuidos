import os
import time
import requests
import logging
from distributions.uniform import generate_uniform
from distributions.normal import generate_normal
from dotenv import load_dotenv
import threading

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TrafficGenerator:
    def __init__(self):
        self.storage_url = os.getenv("STORAGE_SERVICE_URL", "http://storage:5001")
        self.cache_url = os.getenv("CACHE_SERVICE_URL", "http://cache:5002")
        self.stats = {
            'uniform': {'total': 0, 'hits': 0, 'avg_interval': 0},
            'normal': {'total': 0, 'hits': 0, 'avg_interval': 0}
        }

    def get_event(self, distribution):
        """Obtiene evento verificando caché primero"""
        try:
            # Obtener evento del storage
            event = requests.get(f"{self.storage_url}/events/random").json()
            
            # Determinar tipo de caché
            cache_type = distribution.lower()
            
            # Verificar caché
            cache_resp = requests.post(
                f"{self.cache_url}/cache/{cache_type}",
                json={'action': 'get', 'key': event['id']}
            ).json()
            
            self.stats[distribution]['total'] += 1
            
            if cache_resp.get('found'):
                self.stats[distribution]['hits'] += 1
                logger.debug(f"Cache hit ({cache_type}) for event {event['id']}")
            else:
                # Almacenar en caché
                requests.post(
                    f"{self.cache_url}/cache/{cache_type}",
                    json={'action': 'put', 'key': event['id'], 'value': event}
                )
            
            return event
        
        except Exception as e:
            logger.error(f"Error getting event: {e}")
            return None

    def generate_distribution(self, distribution, duration_min=10):
        """Genera tráfico según la distribución especificada"""
        start_time = time.time()
        intervals = []
        
        while time.time() - start_time < duration_min * 60:
            event = self.get_event(distribution)
            if event:
                # Generar intervalo según distribución
                if distribution == 'uniform':
                    interval = generate_uniform()
                else:  # normal
                    interval = generate_normal()
                
                intervals.append(interval)
                time.sleep(interval)
                
                # Loggear estadísticas cada 50 eventos
                if self.stats[distribution]['total'] % 50 == 0:
                    self.log_stats(distribution, intervals)
        
        return intervals

    def log_stats(self, distribution, intervals):
        """Muestra estadísticas de rendimiento"""
        stats = self.stats[distribution]
        if stats['total'] > 0:
            hit_rate = (stats['hits'] / stats['total']) * 100
            avg_interval = sum(intervals[-50:]) / len(intervals[-50:]) if intervals else 0
            
            # Obtener stats del caché
            try:
                cache_stats = requests.get(f"{self.cache_url}/cache/stats").json()
                cache_info = cache_stats[f"{distribution}_cache"]
                
                logger.info(
                    f"\n=== {distribution.upper()} STATS ===\n"
                    f"Requests: {stats['total']} | "
                    f"Cache hits: {stats['hits']} ({hit_rate:.1f}%)\n"
                    f"Avg interval: {avg_interval:.2f}s\n"
                    f"Cache usage: {cache_info['current_bytes']/1024:.1f}KB/"
                    f"{cache_info['max_bytes']/1024:.1f}KB "
                    f"({cache_info['current_bytes']/cache_info['max_bytes']*100:.1f}%)\n"
                    f"Cache policy: {cache_info['policy']} | "
                    f"Items in cache: {cache_info['items_count']}\n"
                    "===================="
                )
            except Exception as e:
                logger.error(f"Error getting cache stats: {e}")

def run_generator():
    try:
        generator = TrafficGenerator()
        logger.info("Starting traffic generator...")
        
        # Crear hilos para cada distribución
        uniform_thread = threading.Thread(
            target=generator.generate_distribution,
            args=('uniform', 5)  # 5 minutos
        )
        
        normal_thread = threading.Thread(
            target=generator.generate_distribution,
            args=('normal', 5)  # 5 minutos
        )
        
        # Iniciar generadores
        uniform_thread.start()
        normal_thread.start()
        
        # Esperar finalización
        uniform_thread.join()
        normal_thread.join()
        
        # Estadísticas finales
        logger.info("=== FINAL STATISTICS ===")
        for dist in generator.stats:
            total = generator.stats[dist]['total']
            hits = generator.stats[dist]['hits']
            if total > 0:
                logger.info(
                    f"{dist.upper()} - Final hit rate: {(hits/total)*100:.1f}%"
                )
    except Exception as e:
        logger.error(f"Generator error: {e}")
        raise

if __name__ == '__main__':
    run_generator()