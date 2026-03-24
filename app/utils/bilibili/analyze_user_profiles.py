from app.database.redis_client import RedisClient
from app.utils.agent.openai_client import OpenaiClient
from datetime import datetime
from typing import List, Optional, Dict, Any
import json

redis_client = RedisClient()


def get_user_comments_from_redis(uid: int | str) -> List[Dict[str, Any]]:
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
            print(f"Redis数据解析失败: {e}")
            return []
    return []

async def analyze_user_comments(uid: int | str) -> Dict[str, Any]:
    """
    使用大模型API分析用户评论，生成用户画像
    """
    print("调用分析画像函数")
    if redis_client.get_client().exists(f"analysis_{uid}"):
        return {"msg": "分析过了"}
    if uid == int(redis_client.get('last_huaxiang')): # type: ignore
        print("重复提交")
        return {"msg": "已经在分析了"}
    redis_client.set('last_huaxiang', uid)

    try:
        # 从Redis获取评论
        comments = get_user_comments_from_redis(uid)
        print(f"从Redis获取到 {len(comments)} 条评论")
        
        if not comments:
            return {"error": "未找到用户评论数据"}
        
        # 提取评论文本
        comment_texts = []
        for i, comment in enumerate(comments):
            comment_text = comment.get('comment_text', '')
            if comment_text and comment_text.strip():
                comment_texts.append(comment_text)
        
        print(f"有效评论数量: {len(comment_texts)}")
        
        if not comment_texts:
            return {"error": "评论内容为空，请检查评论数据格式"}
        
        # 限制评论数量，避免token过多
        sample_comments = comment_texts[:20]  # 取前20条评论
        comments_text = "\n".join([f"{i+1}. {comment}" for i, comment in enumerate(sample_comments)])
        
        # 构建分析提示词
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
        
        # 使用高质量默认模型
        model_to_use = "qwen3-max"
        
        print(f"开始使用 OpenaiClient 分析用户 {uid} 的评论，模型: {model_to_use}")
        
        # 调用AI接口
        response = await client.chat(
            messages=[{"role": "user", "content": user_prompt}],
            model=model_to_use,
            system_prompt=system_prompt
        )
        
        if response and "choices" in response:
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
            print(f"用户 {uid} 画像分析完成")
            
            return analysis_result
        else:
            error_msg = response.get("error", "未知错误") if response else "响应为空"
            print(f"OpenaiClient 调用失败: {error_msg}")
            return {"error": f"智能分析失败: {error_msg}"}
            
    except Exception as e:
        print(f"分析用户评论时发生错误: {e}")
        return {"error": f"分析失败: {str(e)}"}
    finally:
        redis_client.set('last_huaxiang', 0)

def get_user_analysis_from_redis(uid: int | str) -> Dict[str, Any]:
    """
    从Redis获取用户画像分析结果，优先查找{uid}_result，其次查analysis_{uid}
    """

    data = redis_client.get(f"{uid}_result")
    if not data:
        data = redis_client.get(f"analysis_{uid}")
    if data:
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            if not isinstance(data, str):
                return {}
            return json.loads(data)
        except Exception as e:
            print(f"Redis分析数据解析失败: {e}")
            return {}
    return {}
