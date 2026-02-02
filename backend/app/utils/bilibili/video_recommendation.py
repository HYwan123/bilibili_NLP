from app.database.redis_client_async import RedisClientAsync
import json
import httpx
redis = RedisClientAsync()

VECTOR_INSRET = "streams_insert_bv"
VECTOR_TUIJIAN = "streams_vector_tuijian"
VECTOR_TUIJIAN_RESULT = "streams_vector_tuijian_RESULT"

async def insert_vector_by_BV(BVid: str) -> None:
    await redis.add_streams(VECTOR_INSRET, {"BV": BVid})

async def get_tuijian_bvs(user_id: str) -> list[str] | None:
    await redis.add_streams(VECTOR_TUIJIAN, {"user_id": user_id})
    while True:
        data = await redis.get_streams(VECTOR_TUIJIAN_RESULT)
        if redis.get_streams_dict(data)["user_id"] == user_id:
            return json.loads(redis.get_streams_dict(data)["data"])


async def get_video_info(BVid: str) -> dict:
    cookie = await redis.get('cookie_video_info')
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={BVid}"
    headers = {
        'Cookie': cookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i'
    }
    async with httpx.AsyncClient() as requests:
        response = await requests.get(url, headers=headers)
    print(f"API响应状态码: {response.status_code}")
    print(f"API响应内容: {response.text[:200]}...")  # 只打印前200字符避免过长
    
    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 0:  # B站API成功返回code=0
            video_data = data['data']
            return {
                'msg': 'OK',
                'title': video_data.get('title', ''),
                'desc': video_data.get('desc', ''),
                'tname': video_data.get('tname', '未知分类'),
                'pic': video_data.get('pic', ''),
                'view': video_data.get('stat', {}).get('view', 0),
                'reply': video_data.get('stat', {}).get('reply', 0),
                'favorite': video_data.get('stat', {}).get('favorite', 0),
                'coin': video_data.get('stat', {}).get('coin', 0),
                'owner': {'name': video_data.get('owner', {}).get('name', '未知')},
                'pubdate': video_data.get('pubdate', 0),
                'duration': video_data.get('duration', 0)
            }
        else:
            print(f"B站API返回错误: {data.get('message', '未知错误')}")
            return {'msg': 'fail'}
    else:
        print(f"HTTP请求失败，状态码: {response.status_code}")
        return {'msg': 'fail'}
    
        
