import redis.asyncio as redis
import asyncio

class RedisClientAsync:
    _instance = None
    _isconnected = False

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, host='localhost', port=6379, db=0):
        if not RedisClientAsync._isconnected:
            try:
                self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
                RedisClientAsync._isconnected = True
                print("Successfully connected to Redis.")
            except Exception as e:
                print(f"Failed to connect to Redis: {e}")
                self.redis_client = False


    async def test(self):
        return await self.redis_client.get('test') # type: ignore

    



async def main() -> None:
    redis_client = RedisClientAsync()
    result = await redis_client.test()
    print(result)

if __name__ == '__main__':
    asyncio.run(main())