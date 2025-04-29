from flask import Flask, request, jsonify
from policies.lru import LRUCache
from policies.lfu import LFUCache
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configurar caches con límites en bytes
UNIFORM_CACHE = LRUCache(max_bytes=int(os.getenv('UNIFORM_CACHE_BYTES', 102400)))  # 100KB
NORMAL_CACHE = LFUCache(max_bytes=int(os.getenv('NORMAL_CACHE_BYTES', 51200)))    # 50KB

@app.route('/cache/uniform', methods=['POST'])
def handle_uniform():
    data = request.json
    action = data.get('action')
    key = data.get('key')
    
    if action == 'get':
        value = UNIFORM_CACHE.get(key)
        return jsonify({
            'found': value is not None,
            'value': value if value else None,
            'cache': 'LRU',
            'size_bytes': UNIFORM_CACHE.current_size(),
            'max_bytes': UNIFORM_CACHE.max_bytes
        })
    elif action == 'put':
        UNIFORM_CACHE.put(key, data.get('value'))
        return jsonify({
            'status': 'added',
            'cache': 'LRU',
            'size_bytes': UNIFORM_CACHE.current_size(),
            'max_bytes': UNIFORM_CACHE.max_bytes
        })
    return jsonify({'error': 'invalid action'}), 400

@app.route('/cache/normal', methods=['POST'])
def handle_normal():
    data = request.json
    action = data.get('action')
    key = data.get('key')
    
    if action == 'get':
        value = NORMAL_CACHE.get(key)
        return jsonify({
            'found': value is not None,
            'value': value if value else None,
            'cache': 'LFU',
            'size_bytes': NORMAL_CACHE.current_size(),
            'max_bytes': NORMAL_CACHE.max_bytes
        })
    elif action == 'put':
        NORMAL_CACHE.put(key, data.get('value'))
        return jsonify({
            'status': 'added',
            'cache': 'LFU',
            'size_bytes': NORMAL_CACHE.current_size(),
            'max_bytes': NORMAL_CACHE.max_bytes
        })
    return jsonify({'error': 'invalid action'}), 400

@app.route('/cache/stats', methods=['GET'])
def cache_stats():
    return jsonify({
        'uniform_cache': {
            'policy': 'LRU',
            'current_bytes': UNIFORM_CACHE.current_size(),
            'max_bytes': UNIFORM_CACHE.max_bytes,
            'items_count': len(UNIFORM_CACHE)
        },
        'normal_cache': {
            'policy': 'LFU',
            'current_bytes': NORMAL_CACHE.current_size(),
            'max_bytes': NORMAL_CACHE.max_bytes,
            'items_count': len(NORMAL_CACHE)
        }
    })

# Añadir endpoint de healthcheck
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Verificar que ambos caches están inicializados
        return jsonify({
            "status": "healthy",
            "uniform_cache_size": UNIFORM_CACHE.current_size(),
            "normal_cache_size": NORMAL_CACHE.current_size()
        })
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)