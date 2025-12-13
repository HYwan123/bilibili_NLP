import asyncio
from app.database.redis_client_async import RedisClientAsync
from backend.app.worker.utils import comment_analyzer
import json

STREAMS_NAME = "streams_analyze_video_comments"



async def main() -> None:
    redis_client = RedisClientAsync()
    while True:
        xread_data = await redis_client.get_streams(STREAMS_NAME)
        data = redis_client.get_streams_dict(xread_data)
        id = redis_client.get_streams_id(xread_data)
        bv = data['BV']
        bv_data = await redis_client.get(bv)
        await comment_analyzer.analyze_bv_comments(bv, json.loads(bv_data))
        await redis_client.del_stream_key(STREAMS_NAME, id)




if __name__ == '__main__':
    asyncio.run(main())