from collections import OrderedDict
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FIFOCache:
    def __init__(self, max_bytes=102400):  # 100KB por defecto
        self.max_bytes = max_bytes
        self.current_bytes = 0
        self.cache = OrderedDict()
        logger.info(f"Created FIFO Cache with max {max_bytes} bytes")

    def __sizeof_item(self, item):
        """Calcula tamaño aproximado en bytes de un item"""
        return sys.getsizeof(item[0]) + sys.getsizeof(item[1])  # key + value

    def get(self, key):
        """Obtiene un valor del cache (no afecta el orden)"""
        return self.cache.get(key, None)

    def put(self, key, value):
        """Agrega un item al cache (FIFO)"""
        item_size = self.__sizeof_item((key, value))
        
        if item_size > self.max_bytes:
            logger.warning(f"Item too large ({item_size} bytes) for cache")
            return

        # Eliminar items existentes si es necesario (en orden FIFO)
        while self.current_bytes + item_size > self.max_bytes and self.cache:
            removed_key, removed_val = self.cache.popitem(last=False)
            removed_size = self.__sizeof_item((removed_key, removed_val))
            self.current_bytes -= removed_size
            logger.debug(f"FIFO Cache full. Removed: {removed_key} ({removed_size} bytes)")

        # Agregar nuevo item
        if key in self.cache:
            existing_size = self.__sizeof_item((key, self.cache[key]))
            self.current_bytes -= existing_size
        self.cache[key] = value
        self.current_bytes += item_size

    def __len__(self):
        return len(self.cache)

    def current_size(self):
        return self.current_bytes