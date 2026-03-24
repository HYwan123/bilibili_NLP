import json
from typing import List, Dict, Any, Optional
from app.database.redis_client_async import RedisClientAsync
import asyncio

redis_client = RedisClientAsync()

STREAMS_NAME = "streams_analyze_video_comments"
RESULT_STREAM = "streams_result_isok"

async def analyze_comments(comments: List[Dict[str, Any]], bv_id: str):
    """
    将任务分发给 Worker 并等待结果
    """
    # 1. 确保原始数据已存入 Redis (Worker 需要读这个)
    await redis_client.set(bv_id, json.dumps(comments, ensure_ascii=False))
    
    # 2. 发送任务到 Stream
    await redis_client.add_streams(STREAMS_NAME, {'BV': bv_id})
    
    # 3. 轮询等待结果 (Worker 完成后会写入 comment_analysis_{bv_id})
    # 我们不再直接监听 RESULT_STREAM，因为在高并发下容易发生偏移错误
    # 改为更稳健的 Key 轮询
    max_retries = 60 # 约 2 分钟超时
    for _ in range(max_retries):
        analysis_data = await redis_client.get(f"comment_analysis_{bv_id}")
        if analysis_data:
            try:
                result = json.loads(analysis_data)
                # 检查是否包含报错信息
                if isinstance(result, dict):
                    return result
            except Exception:
                pass
        await asyncio.sleep(2)
    
    return {"error": "分析引擎响应超时"}
    
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
    return await analyze_comments(comments, bv_id)

async def get_bv_analysis(bv_id: str) -> Dict[str, Any]:
    """
    便捷函数：获取BV评论分析结果
    """
    return await get_analysis_from_redis(bv_id)
