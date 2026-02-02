import json
from typing import List, Dict, Any
from app.database.redis_client_async import RedisClientAsync

redis_client = RedisClientAsync()

STREAMS_NAME = "streams_analyze_video_comments"
RESULT_STREAM = "streams_result_isok"

async def analyze_comments(comments, bv_id):
    await redis_client.add_streams(STREAMS_NAME, {'BV': bv_id})
    ok_bv_data = await redis_client.get_streams(RESULT_STREAM)
    ok_bv = redis_client.get_streams_dict(ok_bv_data['BV'])
    
    if ok_bv == bv_id:
        streams_id = redis_client.get_streams_id(ok_bv_data)
        await redis_client.del_stream_key(RESULT_STREAM, streams_id)
        data = await redis_client.get(f"comment_analysis_{bv_id}")
        return json.loads(data) 
    
async def get_analysis_from_redis(bv_id: str) -> Dict[str, Any]:
    """
    从Redis获取评论分析结果
    """
    data = await redis_client.get(f"comment_analysis_{bv_id}")
    if data:
        try:
            return json.loads(data) # type: ignore
        except Exception as e:
            print(f"Redis数据解析失败: {e}")
            return {}
    return {}

async def analyze_bv_comments(bv_id: str, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    便捷函数：分析BV评论
    """

    return await analyze_comments(comments, bv_id) #type: ignore

async def get_bv_analysis(bv_id: str) -> Dict[str, Any]:
    """
    便捷函数：获取BV评论分析结果
    """

    return await get_analysis_from_redis(bv_id)
