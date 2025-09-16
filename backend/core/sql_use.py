import redis
import json
import mysql.connector
from typing import List, Dict, Any, Optional

# --- Database Configuration ---
DB_CONFIG = {
    'user': 'your_username',
    'password': 'your_password',
    'host': '127.0.0.1',
    'database': 'bilibili_comment',
    'port': 3306
}

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Failed to connect to MySQL: {err}")
        return None

class SQL_redis:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SQL_redis, cls).__new__(cls)
        return cls._instance

    def __init__(self, host='localhost', port=6379, db=0):
        if not hasattr(self, 'redis_client'):
            try:
                self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=False)
                self.redis_client.ping()
                print("Successfully connected to Redis.")
            except redis.exceptions.ConnectionError as e: # type: ignore
                print(f"Failed to connect to Redis: {e}")
                self.redis_client = None

    def get_client(self) -> Optional[redis.Redis]:
        """Returns the raw Redis client instance."""
        return self.redis_client

    def redis_insert(self, name: str, value: List[Dict[str, Any]]):
        if not self.redis_client: return
        serialized_value = json.dumps(value)
        self.redis_client.set(name, serialized_value)

    def redis_select_by_key(self, name: str) -> Any:
        if not self.redis_client: return None
        return self.redis_client.get(name)

    def redis_set_by_key(self, name: str, value: Any) -> bool:
        if not self.redis_client: return False
        # 序列化非基本类型的数据
        if isinstance(value, (list, dict)):
            value = json.dumps(value)
        # 确保值是bytes类型
        if isinstance(value, str):
            value = value.encode('utf-8')
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


class SQL_mysql:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host = '127.0.0.1',
            user = 'wan',
            password = 'Qqwe123123',
            database = 'bilibili_NLP'
        )
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def close(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()


    def test(self):
        self.cursor.execute('SELECT * FROM test')
        rows = self.cursor.fetchall()
        print(1)
        for row in rows:
            print(row)



def main() -> None:
    sql_m = SQL_redis()
    print(sql_m.redis_select('BV1cN411e7SG'))


if __name__ == '__main__':
    main()
