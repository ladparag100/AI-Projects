import time

class SchemaCache:
    """Simple TTL-based cache for Notion database schemas."""
    def __init__(self, ttl=3600):
        self.ttl = ttl
        self._cache = {}

    def get(self, database_id):
        if database_id in self._cache:
            entry = self._cache[database_id]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['schema']
        return None

    def set(self, database_id, schema):
        self._cache[database_id] = {
            'schema': schema,
            'timestamp': time.time()
        }

    def clear(self):
        self._cache.clear()

schema_cache = SchemaCache()