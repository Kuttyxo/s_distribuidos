import os
import time
import requests
import logging
import random
import threading
from collections import deque
from distributions.uniform import generate_uniform
from distributions.normal import generate_normal
from dotenv import load_dotenv

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
        
        # Estadísticas con bloqueo para thread safety
        self.stats = {
            'uniform': {'total': 0, 'hits': 0, 'intervals': [], 'lock': threading.Lock()},
            'normal': {'total': 0, 'hits': 0, 'intervals': [], 'lock': threading.Lock()}
        }
        
        # Buffer controlado para distribución normal
        self.normal_buffer = deque(maxlen=int(os.getenv("BUFFER_SIZE", "12")))
        self.buffer_lock = threading.Lock()
        self.running = True

    def get_event(self, distribution):
        """Obtiene evento con buffer controlado para normal"""
        try:
            event = None
            
            # Solo usar buffer para distribución normal con probabilidad controlada
            if distribution == 'normal' and random.random() < float(os.getenv("NORMAL_REUSE_PROBABILITY", "0.25")):
                with self.buffer_lock:
                    if self.normal_buffer:
                        event = random.choice(self.normal_buffer)
                        logger.debug(f"Reusing buffered event: {event['id']}")
            
            if not event:
                event = requests.get(f"{self.storage_url}/events/random").json()
                if distribution == 'normal':
                    with self.buffer_lock:
                        self.normal_buffer.append(event)
            
            # Proceso de caché
            cache_type = distribution.lower()
            with self.stats[distribution]['lock']:
                self.stats[distribution]['total'] += 1
                
                cache_resp = requests.post(
                    f"{self.cache_url}/cache/{cache_type}",
                    json={'action': 'get', 'key': event['id']},
                    timeout=2
                ).json()
                
                if cache_resp.get('found'):
                    self.stats[distribution]['hits'] += 1
                else:
                    requests.post(
                        f"{self.cache_url}/cache/{cache_type}",
                        json={'action': 'put', 'key': event['id'], 'value': event},
                        timeout=2
                    )
            
            return event
        
        except Exception as e:
            logger.error(f"Error getting event: {e}")
            return None

    def generate_distribution(self, distribution, duration_min=30):
        """Generador con intervalo controlado"""
        start_time = time.time()
        last_log_time = start_time
        
        while self.running and (time.time() - start_time < duration_min * 60):
            event = self.get_event(distribution)
            if event:
                interval = generate_uniform() if distribution == 'uniform' else generate_normal()
                time.sleep(interval)
                
                with self.stats[distribution]['lock']:
                    self.stats[distribution]['intervals'].append(interval)
                
                if time.time() - last_log_time >= 30:
                    self.log_stats(distribution)
                    last_log_time = time.time()

    def log_stats(self, distribution):
        """Log de estadísticas mejorado"""
        try:
            with self.stats[distribution]['lock']:
                stats = self.stats[distribution]
                total = stats['total']
                hits = stats['hits']
                
                if total > 0:
                    hit_rate = (hits / total) * 100
                    avg_interval = sum(stats['intervals'])/len(stats['intervals']) if stats['intervals'] else 0
                    
                    cache_stats = requests.get(f"{self.cache_url}/cache/stats", timeout=2).json()
                    cache_info = cache_stats[f"{distribution}_cache"]
                    
                    logger.info(
                        f"\n=== {distribution.upper()} STATS ===\n"
                        f"Total Requests: {total} | "
                        f"Cache Hits: {hits} ({hit_rate:.1f}%)\n"
                        f"Avg Interval: {avg_interval:.2f}s\n"
                        f"Cache Usage: {cache_info['current_bytes']/1024:.1f}KB/"
                        f"{cache_info['max_bytes']/1024:.1f}KB\n"
                        f"Cache Policy: {cache_info['policy']} | "
                        f"Items: {cache_info['items_count']}\n"
                        f"Buffer Usage: {len(self.normal_buffer)}/{os.getenv('BUFFER_SIZE', '12') if distribution == 'normal' else 'N/A'}\n"
                        "===================="
                    )
                    
                    stats['intervals'] = []
        
        except Exception as e:
            logger.error(f"Error logging stats: {e}")

    def stop(self):
        self.running = False

def run_generator():
    generator = TrafficGenerator()
    
    try:
        logger.info("Starting generator with controlled buffer...")
        
        threads = [
            threading.Thread(target=generator.generate_distribution, args=('uniform', 30)),
            threading.Thread(target=generator.generate_distribution, args=('normal', 30))
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
    except KeyboardInterrupt:
        logger.info("\nStopping generator...")
        generator.stop()
        for t in threads:
            t.join(timeout=1)
    finally:
        logger.info("\n=== FINAL STATISTICS ===")
        generator.log_stats('uniform')
        generator.log_stats('normal')

if __name__ == '__main__':
    run_generator()