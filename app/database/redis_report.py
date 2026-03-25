import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import time
import database
from app.database.redis_pool import get_redis_client
from app.database.mysql_exceptions import log_error
from app.utils.agent.openai_client import OpenaiClient
import logging

# Configure logging
logger = logging.getLogger(__name__)

redis_client = get_redis_client()


def get_user_comments_from_redis(uid: int) -> List[Dict[str, Any]]:
    """
    从Redis获取用户评论
    """
    data = redis_client.get(str(uid))
    if data:
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            if not isinstance(data, str):
                return []
            return json.loads(data)
        except Exception as e:
            logger.error(f"Redis数据解析失败: {e}")
            return []
    return []

async def analyze_user_comments(uid: int) -> Dict[str, Any]:
    """
    使用大模型API分析用户评论，生成用户画像
    """
    try:
        # 从Redis获取评论
        comments = get_user_comments_from_redis(uid)
        logger.info(f"从Redis获取到 {len(comments)} 条评论")

        if not comments:
            return {"error": "未找到用户评论数据"}

        # 提取评论文本
        comment_texts = []
        for i, comment in enumerate(comments):
            comment_text = comment.get('comment_text', '')
            if comment_text and comment_text.strip():
                comment_texts.append(comment_text)

        logger.info(f"有效评论数量: {len(comment_texts)}")

        if not comment_texts:
            return {"error": "评论内容为空，请检查评论数据格式"}

        # 限制评论数量，避免token过多
        sample_comments = comment_texts[:20]  # 取前20条评论
        comments_text = "\n".join([f"{i+1}. {comment}" for i, comment in enumerate(sample_comments)])

        # 构建提示词
        system_prompt = "你是一个专业的 B 站用户行为分析专家。你的任务是根据提供的用户评论数据，构建深度、准确的用户画像报告。"
        user_prompt = f"""请分析以下B站用户的评论内容，生成用户画像分析报告。请从以下几个方面进行分析：

1. 用户兴趣偏好
2. 活跃程度和参与度
3. 评论风格和特点
4. 可能关注的领域
5. 用户性格特征

用户评论内容：
{comments_text}

请用中文回答，确保报告结构清晰、洞察深刻，使用 Markdown 格式渲染。"""

        # 初始化OpenAI客户端
        client = OpenaiClient()
        
        logger.info(f"开始使用 OpenaiClient 分析用户 {uid} 的评论...")
        
        response = await client.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system_prompt=system_prompt
        )

        try:
            if response:
                # 检查响应对象是否包含有效结果
                if hasattr(response, 'choices') and response.choices:
                    analysis_content = client.get_message_content(response)

                    analysis_result = {
                        "uid": uid,
                        "comment_count": len(comments),
                        "analysis": analysis_content,
                        "sample_comments": sample_comments,
                        "timestamp": datetime.now().isoformat()
                    }

                    # 将分析结果保存到Redis的两种key
                    redis_client.set(f"analysis_{uid}", json.dumps(analysis_result, ensure_ascii=False))
                    redis_client.set(f"{uid}_result", json.dumps(analysis_result, ensure_ascii=False))
                    logger.info(f"用户 {uid} 画像分析完成")

                    return analysis_result
                else:
                    error_msg = "AI响应中没有有效内容" if response else "响应为空"
                    logger.error(f"OpenaiClient 调用失败: {error_msg}")
                    return {"error": f"智能分析失败: {error_msg}"}
            else:
                logger.error("OpenaiClient 调用失败: 响应为空")
                return {"error": "智能分析失败: 响应为空"}
        except Exception as e:
            logger.error(f"处理AI响应时发生错误: {e}")
            return {"error": f"智能分析失败: {str(e)}"}

    except Exception as e:
        logger.error(f"分析用户评论时发生错误: {e}")
        log_error(e, "analyze_user_comments")
        return {"error": f"分析失败: {str(e)}"}




async def analyze_user_portrait(uid: int):
    """
    分析用户评论，生成用户画像
    """
    try:
        result = await analyze_user_comments(uid)

        if "error" in result:
            return 'error'


        logger.info('分析完成')
        return 'OK'

    except Exception as e:
        logger.error(f"用户画像分析失败: {e}")
        log_error(e, "analyze_user_portrait")
        return 'error'

async def create_report() -> None:
    r = get_redis_client()
    while True:
        # 建议这里使用异步非阻塞或 sleep
        await asyncio.sleep(5)
        uid = r.lpop('uids')
        if not uid:
            continue
            
        if redis_client.get(f'{uid}_result') or redis_client.get(f'analysis_{uid}'):
            logger.info(f"用户 {uid} 已经分析过了")
        else:
            logger.info(f"正在分析新用户: {uid}")
            await analyze_user_portrait(int(uid)) # type: ignore
            database.add_report_history(int(uid)) # type: ignore

import asyncio
def main() -> None:
    asyncio.run(create_report())

if __name__ == '__main__':
    main()
