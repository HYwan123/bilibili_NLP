from typing import List, Optional, Dict, Any, cast
import subprocess
from app.database.redis_client import RedisClient
import json
import httpx

redis_handler = RedisClient()

def get_user_comments_simple_1(uid: int | str) -> List[Dict[str, Any]]:
    """
    简单的用户评论获取函数，使用subprocess调用curl，直接获取评论数据，并保存到Redis
    """
    try:
        print(f"开始获取用户 {uid} 的评论...")
        cmd = [
            "curl",
            f"https://api.aicu.cc/api/v3/search/getreply?uid={uid}&ps=100&pn=1&mode=0&keyword="
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            print(f"curl命令执行失败: {result.stderr}")
            return []
        if not result.stdout.strip():
            print(f"API返回空数据 for UID {uid}")
            return []
        data = json.loads(result.stdout)
        replies = data.get('data', {}).get('replies', [])
        if not replies:
            print(f"API返回空评论数据 for UID {uid}")
            return []
        user_comments = [{'comment_text': reply.get('message')} for reply in replies if reply.get('message')]
        print(f"成功获取 {len(user_comments)} 条评论 for UID {uid}")
        # 保存到Redis
        redis_handler.set(str(uid), json.dumps(user_comments, ensure_ascii=False))
        print(f"已保存到Redis，key={uid}")
        return user_comments
    except subprocess.TimeoutExpired:
        print(f"curl命令超时 for UID {uid}")
        return []
    except subprocess.CalledProcessError as e:
        print(f"curl命令执行失败 for UID {uid}: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON解析失败 for UID {uid}: {e}")
        print(f"响应内容: {result.stdout}...")
        return []
    except Exception as e:
        print(f"获取评论时发生未知错误 for UID {uid}: {e}")
        return []

def get_user_comments_simple(uid: int | str) -> List[Dict[str, Any]]:
    """
    简单的用户评论获取函数，使用subprocess调用curl，直接获取评论数据，并保存到Redis
    """
    try:
        headers = {
            "cookie": redis_handler.get("cookie_aicu")
            }
        headers = cast(dict[str, str], headers)
        result = httpx.get(f"https://api.aicu.cc/api/v3/search/getreply?uid={uid}&ps=100&pn=1&mode=0&keyword=", headers=headers)
        print(f"开始获取用户 {uid} 的评论...")
        print(result.json())
        data = result.json()
        replies = data.get('data', {}).get('replies', [])
        if not replies:
            print(f"API返回空评论数据 for UID {uid}")
            return []
        user_comments = [{'comment_text': reply.get('message')} for reply in replies if reply.get('message')]
        print(f"成功获取 {len(user_comments)} 条评论 for UID {uid}")
        # 保存到Redis
        redis_handler.set(str(uid), json.dumps(user_comments, ensure_ascii=False))
        print(f"已保存到Redis，key={uid}")
        return user_comments

    except json.JSONDecodeError as e:
        print(f"JSON解析失败 for UID {uid}: {e}")
        print(f"响应内容: {result}...")
        return []
    except Exception as e:
        print(f"获取评论时发生未知错误 for UID {uid}: {e}")
        return []

