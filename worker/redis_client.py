import redis.asyncio as redis
import asyncio

class RedisClientAsync:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance    
    
    def __init__(self, host='localhost', port=6379, db=0):
        if not hasattr(self, "redis_client"):
            self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    async def test(self):
        try:
            return await self.redis_client.get('test')
        except Exception as e:
            print("Redis error:", e)

    async def add_streams(self, key: str, value: dict):
        try:
            return await self.redis_client.xadd(key, value)
        except Exception as e:
            print("Redis error:", e)

    async def get(self, key):
        return await self.redis_client.get(key)


    async def get_streams(self, key):
        return await self.redis_client.xread({key: "0"}, count=1, block=0) # type: ignore

    @staticmethod
    def get_streams_dict(xread_result: list):
        return xread_result[0][1][0][1]
    
    @staticmethod
    def get_streams_id(xread_result: list):
        return xread_result[0][1][0][0]

async def main():
    redis_client = RedisClientAsync()
    #await redis_client.add_streams('test_streams', {'test1': 1, 'test2': 2})
    result = await redis_client.get_streams('test_streams')
    print(redis_client.get_streams_dict(result))

if __name__ == '__main__':
    asyncio.run(main())
