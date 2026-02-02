import redis
import os
import logging
from typing import Optional, Any
import json

# Configure logging
logger = logging.getLogger(__name__)

# Redis configuration using environment variables
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': int(os.getenv('REDIS_DB', 0)),
    'decode_responses': True,
    'max_connections': int(os.getenv('REDIS_MAX_CONNECTIONS', 20))
}

class RedisPool:
    def __init__(self):
        self.pool_config = REDIS_CONFIG
        self.connection_pool = None
        self.client = None
        self._create_pool()

    def _create_pool(self):
        """Create a Redis connection pool"""
        try:
            self.connection_pool = redis.ConnectionPool(**self.pool_config)
            self.client = redis.Redis(connection_pool=self.connection_pool)
            # Test connection
            self.client.ping()
            logger.info("Redis connection pool created successfully")
        except Exception as e:
            logger.error(f"Error creating Redis connection pool: {e}")
            raise

    def get_client(self) -> redis.Redis:
        """Get a Redis client from the pool"""
        if not self.client:
            self._create_pool()
        return self.client #type: ignore

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        try:
            return self.get_client().get(key)
        except Exception as e:
            logger.error(f"Error getting key {key} from Redis: {e}")
            return None

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set value in Redis"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            self.get_client().set(key, value, ex=ex)
            return True
        except Exception as e:
            logger.error(f"Error setting key {key} in Redis: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            self.get_client().delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting key {key} from Redis: {e}")
            return False

    def lpush(self, key: str, value: Any) -> bool:
        """Push value to the left of a list in Redis"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
                self.get_client().lpush(key, value)
                return True
        except Exception as e:
            logger.error(f"Error pushing to list {key} in Redis: {e}")
            return False
        return False

    def lpop(self, key: str) -> Optional[Any]:
        """Pop value from the left of a list in Redis"""
        try:
            return self.get_client().lpop(key)
        except Exception as e:
            logger.error(f"Error popping from list {key} in Redis: {e}")
            return None

# Global Redis pool instance
redis_pool = RedisPool()

def get_redis_client():
    """Get a Redis client from the pool"""
    return redis_pool.get_client()