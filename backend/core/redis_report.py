import requests
import json
from typing import List, Optional, Dict, Any
import redis
from datetime import datetime
import time
import database
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


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

def analyze_user_comments(uid: int) -> Dict[str, Any]:
    """
    使用大模型API分析用户评论，生成用户画像
    """
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

        # 调用大模型API
        api_url = "https://api.siliconflow.cn/v1/chat/completions"
        headers = {
            "Authorization": "Bearer sk-skgydfquljaaecqxaqyumvbhnurbzqovgynlvcadxwpfifux",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "Qwen/QwQ-32B",
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
        response = requests.post(api_url, headers=headers, json=data, timeout=160)
        
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




def analyze_user_portrait(uid: int):
    """
    分析用户评论，生成用户画像
    """
    try:
        result = analyze_user_comments(uid)
        
        if "error" in result:
            return 'error'
        
       
        print('分析完成')
        return 'OK'
        
    except Exception as e:
        print(f"用户画像分析失败: {e}")
        return 'error'

def create_report() -> None:
    r = redis.Redis(host='127.0.0.1', db=0, decode_responses=True)
    while True:
        time.sleep(5)
        uid = r.lpop('uids')
        if redis_client.get(f'{uid}_result') or redis_client.get(f'analysis_{uid}'):
            print("分析过了")       
        else:
            if uid is not None:
                analyze_user_portrait(uid) # type: ignore
                database.add_report_history(uid) # type: ignore

    r.close()

def main() -> None:
    create_report()

if __name__ == '__main__':
    main()