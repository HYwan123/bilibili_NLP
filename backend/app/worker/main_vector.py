import json
from sentence_transformers import SentenceTransformer
from app.database.milvus_client import MilvusClient
from app.database.redis_client_async import RedisClientAsync
import httpx
from httpx import AsyncClient
import asyncio

model = SentenceTransformer("BAAI/bge-base-zh")  # 768维

VECTOR_INSRET = "streams_insert_bv"
VECTOR_TUIJIAN = "streams_vector_tuijian"
VECTOR_TUIJIAN_RESULT = "streams_vector_tuijian_RESULT"


async def insert_vector_by_BV(BVid: str, client: AsyncClient, redis: RedisClientAsync, milvus: MilvusClient) -> None:
    tags = await get_video_tags(BVid, client, redis)
    tags_str = " ".join(tags)
    embeddings = model.encode(tags_str).tolist()
    await milvus.insert_vector([BVid], [embeddings])

async def get_tuijian_bvs(user_id: str, redis: RedisClientAsync, milvus: MilvusClient) -> list[str] | None:
    raw = await redis.get(user_id)  # bytes
    if not raw:
        return None
    comments = json.loads(raw)
    all_text = " ".join(comment["comment_text"] for comment in comments)
    results = await milvus.search_similar(model.encode(all_text).tolist())
    return results

    
async def get_video_tags(BVid: str, client: AsyncClient, redis: RedisClientAsync) -> list[str]:
    cookie = await redis.get('cookie_video_info') 
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Cookie": cookie
    }

    json_data = await client.get(url=f'https://api.bilibili.com/x/tag/archive/tags?bvid={BVid}', headers=headers)
    print(json_data)
    json_data = json_data.json()
    try:
        tags = [tag["tag_name"] for tag in json_data["data"]]
        return tags
    except:
        return ['error']



async def worker_insert_vector(redis: RedisClientAsync, millvus: MilvusClient):


    async with httpx.AsyncClient() as client:
        while True:
            data = await redis.get_streams(VECTOR_INSRET)
            bv_id = redis.get_streams_dict(data)["BV"]
            await insert_vector_by_BV(bv_id, client, redis, millvus)

async def worker_get_tuijian_bvs(redis: RedisClientAsync, millvus: MilvusClient):
    while True:
        data = await redis.get_streams(VECTOR_TUIJIAN)
        user_id = redis.get_streams_dict(data)['user_id']
        result = await get_tuijian_bvs(user_id, redis, millvus)
        await redis.add_streams(VECTOR_TUIJIAN_RESULT, {'user_id': user_id, 'data': json.dumps(result)})


async def main() -> None:
    redis = RedisClientAsync()
    millvus = MilvusClient()

    await asyncio.gather(
        worker_insert_vector(redis, millvus),
        worker_get_tuijian_bvs(redis, millvus)
        )



if __name__ == '__main__':
    asyncio.run(main())