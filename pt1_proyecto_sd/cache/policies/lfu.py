from collections import defaultdict, OrderedDict
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LFUCache:
    def __init__(self, max_bytes=51200):  # 50KB por defecto
        self.max_bytes = max_bytes
        self.current_bytes = 0
        self.min_freq = 0
        self.key_to_val = {}  # {key: value}
        self.key_to_freq = {}  # {key: freq}
        self.freq_to_keys = defaultdict(OrderedDict)  # {freq: {key: None}}
        logger.info(f"Created LFU Cache with max {max_bytes} bytes")

    def __sizeof_item(self, item):
        """Calcula tamaño aproximado en bytes de un item"""
        return sys.getsizeof(item[0]) + sys.getsizeof(item[1])  # key + value

    def get(self, key):
        if key not in self.key_to_val:
            return None
        
        # Actualizar frecuencia
        freq = self.key_to_freq[key]
        self.key_to_freq[key] = freq + 1
        del self.freq_to_keys[freq][key]
        self.freq_to_keys[freq + 1][key] = None
        
        # Actualizar min_freq si es necesario
        if freq == self.min_freq and not self.freq_to_keys[freq]:
            self.min_freq += 1
            
        return self.key_to_val[key]

    def put(self, key, value):
        item_size = self.__sizeof_item((key, value))
        
        if item_size > self.max_bytes:
            logger.warning(f"Item too large ({item_size} bytes) for cache")
            return

        # Eliminar items si es necesario
        while self.current_bytes + item_size > self.max_bytes and self.key_to_val:
            # Encontrar clave menos frecuentemente usada
            evict_key = next(iter(self.freq_to_keys[self.min_freq]))
            # Calcular tamaño y eliminar
            evict_size = self.__sizeof_item((evict_key, self.key_to_val[evict_key]))
            del self.freq_to_keys[self.min_freq][evict_key]
            del self.key_to_val[evict_key]
            del self.key_to_freq[evict_key]
            self.current_bytes -= evict_size
            logger.debug(f"LFU Cache full. Removed: {evict_key} ({evict_size} bytes)")

        # Insertar nuevo item
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