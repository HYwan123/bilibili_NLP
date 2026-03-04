import asyncio
from app.database.redis_client_async import RedisClientAsync
from app.worker.utils import comment_analyzer
import json

STREAMS_NAME = "streams_analyze_video_comments"



async def main() -> None:
    redis_client = RedisClientAsync()
    print("Worker: 评论分析服务已启动，等待任务中...")
    last_id = '$'  # 初始只读新消息，之后根据处理到的ID推进
    
    while True:
        try:
            # 始终使用 last_id 确保不漏掉在处理期间到达的消息
            xread_data = await redis_client.get_streams_from_id(STREAMS_NAME, last_id)
            if not xread_data:
                # 如果当前没有新消息，将 last_id 设为 '$' 保持实时监听
                last_id = '$'
                await asyncio.sleep(1)
                continue
                
            data = redis_client.get_streams_dict(xread_data)
            msg_id = redis_client.get_streams_id(xread_data)
            
            # 更新 last_id，下次从这个消息之后开始读
            last_id = msg_id
            
            if not data or 'BV' not in data:
                await redis_client.del_stream_key(STREAMS_NAME, msg_id)
                continue
                
            bv = data['BV']
            print(f"Worker: 收到分析任务 {bv}")
            
            bv_data = await redis_client.get(bv)
            if bv_data:
                await comment_analyzer.analyze_bv_comments(bv, json.loads(bv_data))
            else:
                print(f"Worker: 未能在缓存中找到 {bv} 的语料数据")
                
            # 处理完后删除该流消息
            await redis_client.del_stream_key(STREAMS_NAME, msg_id)
            
        except Exception as e:
            print(f"Worker: 处理任务时发生错误: {e}")
            await asyncio.sleep(2)




if __name__ == '__main__':
    asyncio.run(main())