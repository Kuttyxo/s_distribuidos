from collections import defaultdict, OrderedDict
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LFUCache:
    def __init__(self, max_bytes=180000):  # 180KB
        self.max_bytes = max_bytes
        self.current_bytes = 0
        self.min_freq = 1  # Frecuencia mínima aumentada
        self.key_to_val = {}
        self.key_to_freq = {}
        self.freq_to_keys = defaultdict(OrderedDict)
        self.eviction_count = 0  # Contador de evicciones
        
    def __sizeof_item(self, item):
        return sys.getsizeof(item[0]) + sys.getsizeof(item[1])
    
    def get(self, key):
        if key not in self.key_to_val:
            return None
        
        freq = self.key_to_freq[key]
        self.key_to_freq[key] = freq + 1
        del self.freq_to_keys[freq][key]
        self.freq_to_keys[freq + 1][key] = None
        
        if freq == self.min_freq and not self.freq_to_keys[freq]:
            self.min_freq += 1
            
        return self.key_to_val[key]
    
    def put(self, key, value):
        item_size = self.__sizeof_item((key, value))
        
        if item_size > self.max_bytes:
            logger.warning(f"Item too large for cache: {item_size} bytes")
            return

        # Evicción más agresiva
        while self.current_bytes + item_size > self.max_bytes * 0.9:  # 90% de uso
            if not self.freq_to_keys[self.min_freq]:
                self.min_freq += 1
                continue
                
            evict_key, _ = self.freq_to_keys[self.min_freq].popitem(last=False)
            evict_size = self.__sizeof_item((evict_key, self.key_to_val[evict_key]))
            del self.key_to_val[evict_key]
            del self.key_to_freq[evict_key]
            self.current_bytes -= evict_size
            self.eviction_count += 1
            logger.debug(f"Evicted key: {evict_key} (freq: {self.min_freq})")

        if key in self.key_to_val:
            existing_size = self.__sizeof_item((key, self.key_to_val[key]))
            self.current_bytes -= existing_size
            self.get(key)  # Actualizar frecuencia
        else:
            self.key_to_freq[key] = 1
            self.freq_to_keys[1][key] = None
            self.min_freq = 1
        
        self.key_to_val[key] = value
        self.current_bytes += item_size

    def __len__(self):
        return len(self.key_to_val)
    
    def current_size(self):
        return self.current_bytes