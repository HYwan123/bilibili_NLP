import redis
import json
from typing import List, Dict, Any, Optional
import logging
logger = logging.getLogger(__name__)
class RedisClient:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, host='localhost', port=6379, db=0):
        if not hasattr(self, 'redis_client'):
            try:
                self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
                self.redis_client.ping()
                print("Successfully connected to Redis.")
            except redis.exceptions.ConnectionError as e: # type: ignore
                print(f"Failed to connect to Redis: {e}")
                self.redis_client = None

    
    def redis_insert(self, name: str, value: List[Dict[str, Any]]):
        if not self.redis_client: return
        serialized_value = json.dumps(value)
        self.redis_client.set(name, serialized_value)

    def redis_select_by_key(self, name: str) -> Any:
        if not self.redis_client: return None
        return self.redis_client.get(name)

    def redis_set_by_key(self, name: str, value: Any) -> bool:
        if not self.redis_client: return False
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.redis_client.set(name, value) 
        return True

    def redis_value_add(self, name: str) -> bool:
        try:
            tmp = int(self.redis_select_by_key(name))
            tmp += 1
            self.redis_set_by_key(name, tmp)
            return True
        except:
            return False

    def redis_select(self, name: str) -> Optional[List[Dict[str, Any]]]:
        if not self.redis_client: return None
        serialized_value = self.redis_client.get(name)
        if serialized_value:
            return json.loads(serialized_value) # type: ignore
        return None

    def set_job_status(self, job_id: str, status: Dict[str, Any], ttl: int = 3600):
        if not self.redis_client: return
        key = f"job_status:{job_id}"
        value = json.dumps(status)
        self.redis_client.set(key, value, ex=ttl)

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        if not self.redis_client: return None
        key = f"job_status:{job_id}"
        value = self.redis_client.get(key)
        if value:
            return json.loads(value) # type: ignore
        return None

    def acquire_lock(self, lock_key: str, value: str, timeout: int = 300) -> bool:
        """
        Tries to acquire a lock using SET NX.
        Returns True if the lock was acquired, False otherwise.
        """
        if not self.redis_client:
            return False
        # set with nx=True makes it atomic.
        return self.redis_client.set(lock_key, value, ex=timeout, nx=True) # type: ignore

    def release_lock(self, lock_key: str):
        """Releases the specified lock."""
        if self.redis_client:
            self.redis_client.delete(lock_key)

    def __del__(self):
        if hasattr(self, 'redis_client') and self.redis_client:
            self.redis_client.connection_pool.disconnect()


    def get_client(self) -> redis.Redis:
        return self.redis_client #type: ignore

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
