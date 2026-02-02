import httpx
from app.database.redis_client import RedisClient
from datetime import datetime
from typing import List, Optional, Dict, Any
import json

redis_client = RedisClient()


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
            print(f"Redis数据解析失败: {e}")
            return []
    return []

async def analyze_user_comments(uid: int, api_key: Optional[str] = None, api_url: Optional[str] = None, model_id: Optional[str] = None) -> Dict[str, Any]:
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
        
        # 提取评论文本，并添加调试信息
        comment_texts = []
        for i, comment in enumerate(comments):
            comment_text = comment.get('comment_text', '')
            if comment_text and comment_text.strip():  # 确保不是空字符串或只有空格
                comment_texts.append(comment_text)
            else:
                print(f"第{i+1}条评论内容为空或无效: {comment}")
        
        print(f"有效评论数量: {len(comment_texts)}")
        
        if not comment_texts:
            return {"error": "评论内容为空，请检查评论数据格式"}
        
        # 限制评论数量，避免token过多
        sample_comments = comment_texts[:20]  # 取前20条评论
        comments_text = "\n".join([f"{i+1}. {comment}" for i, comment in enumerate(sample_comments)])
        
        # 构建分析提示词
        prompt = f"""请分析以下B站用户的评论内容，生成用户画像分析报告。请从以下几个方面进行分析：\n\n1. 用户兴趣偏好\n2. 活跃程度和参与度\n3. 评论风格和特点\n4. 可能关注的领域\n5. 用户性格特征\n\n用户评论内容：\n{comments_text}\n\n请用中文回答，格式要清晰易读。"""

        # 使用传入的API配置，如果未提供则使用默认配置
        if api_key and api_url:
            # 使用传入的API配置
            api_base_url = api_url.rstrip('/')  # 移除末尾的斜杠
            if not api_base_url.endswith('/v1'):
                api_base_url += '/v1'
            api_endpoint = f"{api_base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        else:
            # 使用默认配置
            api_endpoint = "https://api.siliconflow.cn/v1/chat/completions"
            headers = {
                "Authorization": "Bearer sk-skgydfquljaaecqxaqyumvbhnurbzqovgynlvcadxwpfifux",
                "Content-Type": "application/json"
            }
        
        # 使用传入的模型ID，如果未提供则使用默认模型
        model_to_use = model_id if model_id else "Qwen/QwQ-32B"
        
        data = {
            "model": model_to_use,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "max_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.7
        }
        
        print(f"开始分析用户 {uid} 的评论...")
        async with httpx.AsyncClient(timeout=1600.0) as client:
            response = await client.post(api_endpoint, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            analysis_content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
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
            print(f"大模型API调用失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:200]}...")
            return {"error": f"API调用失败: {response.status_code}"}
            
    except Exception as e:
        print(f"分析用户评论时发生错误: {e}")
        return {"error": f"分析失败: {str(e)}"}
    finally:
        redis_client.set('last_huaxiang', 0)

def get_user_analysis_from_redis(uid: int) -> Dict[str, Any]:
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