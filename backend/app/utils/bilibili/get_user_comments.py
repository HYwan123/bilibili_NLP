from typing import List, Optional, Dict, Any
import subprocess
from app.database.redis_client import RedisClient
import json
import aiohttp
import asyncio

redis_handler = RedisClient()

def user_select(uid: int, job_id: str) -> Optional[List[Dict[str, Any]]]:
    status_update = {"status": "Processing", "progress": 40, "details": f"正在通过cURL获取用户 {uid} 的评论..."}
    redis_handler.set_job_status(job_id, status_update)
    try:
        api_url = f'https://api.aicu.cc/api/v3/search/getreply?uid={uid}&ps=100&pn=1&mode=0&keyword='
        command = [
            'curl',
            '-s',
            '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            api_url
        ]
        
        process = subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
        
        json_str = process.stdout
        data = json.loads(json_str)
        replies = data.get('data', {}).get('replies', [])
        
        if not replies:
            print(f"API (curl) returned no comments for UID {uid}")
            return []
        
        user_comments = [{'comment_text': reply.get('message')} for reply in replies if reply.get('message')]

    except subprocess.CalledProcessError as e:
        print(f"curl command for UID {uid} failed: {e.stderr}")
        raise Exception(f"调用cURL失败: {e.stderr}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON from curl for UID {uid}: {e}")
        raise Exception(f"解析cURL返回数据失败: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during comment fetching for UID {uid}: {e}")
        raise Exception(f"获取评论时发生未知错误: {e}")

    try:
        
        redis_handler.redis_insert(str(uid), user_comments)

        print(f"Stored {len(user_comments)} comments for UID {uid} in Redis cache")
    except Exception as e:
        print(f"Failed to store comments in Redis for UID {uid}: {e}")

    status_update = {"status": "Processing", "progress": 70, "details": "获取评论成功，正在进行AI分析和存储..."}
    redis_handler.set_job_status(job_id, status_update)
    
    try:
        avg_vector_list = []

    except Exception as e:
        print(f"Vector analysis for UID {uid} failed: {e}")
        # Update status to Failed
        error_message = f"AI分析或向量存储失败: {e}"
        status_update = {"status": "Failed", "progress": 100, "details": error_message}
        redis_handler.set_job_status(job_id, status_update)
        raise Exception(error_message)

    # 6. Update status: Completed
    print(f"Successfully processed job {job_id} for UID {uid}.")
    final_result = {
        "average_vector": avg_vector_list,
        "comments": user_comments
    }
    status_update = {
        "status": "Completed", 
        "progress": 100, 
        "details": f"用户 {uid} 画像分析完成",
        "result": final_result
    }
    redis_handler.set_job_status(job_id, status_update)

    return user_comments

def user_select_simple(uid: int, job_id: str) -> Optional[List[Dict[str, Any]]]:
    """
    同步简化版用户评论获取函数，只获取评论数据并存储到Redis，不进行AI分析
    """

    # 1. Update status: Fetching comments
    status_update = {"status": "Processing", "progress": 40, "details": f"正在通过cURL获取用户 {uid} 的评论..."}
    redis_handler.set_job_status(job_id, status_update)

    # 2. Fetch comments using curl via subprocess with better timeout handling
    try:
        api_url = f'https://api.aicu.cc/api/v3/search/getreply?uid={uid}&ps=100&pn=1&mode=0&keyword='
        # Using a list of arguments is safer. Add a User-Agent header to mimic a browser.
        command = [
            'curl',
            '-s', # Silent mode
            '--max-time', '15',  # 15秒超时
            '--connect-timeout', '10',  # 连接超时10秒
            '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            api_url
        ]
        
        print(f"开始获取用户 {uid} 的评论...")
        process = subprocess.run(command, check=True, capture_output=True, text=True, timeout=20)
        
        if not process.stdout.strip():
            print(f"API返回空数据 for UID {uid}")
            # 更新状态为失败
            error_status = {"status": "Failed", "progress": 100, "details": "API返回空数据"}
            redis_handler.set_job_status(job_id, error_status)
            return []
        
        json_str = process.stdout
        data = json.loads(json_str)
        replies = data.get('data', {}).get('replies', [])
        
        if not replies:
            print(f"API (curl) returned no comments for UID {uid}")
            # 更新状态为完成但无数据
            no_data_status = {"status": "Complete", "progress": 100, "details": f"用户 {uid} 暂无评论数据"}
            redis_handler.set_job_status(job_id, no_data_status)
            return []
        
        user_comments = [{'comment_text': reply.get('message')} for reply in replies if reply.get('message')]
        print(f"成功获取 {len(user_comments)} 条评论 for UID {uid}")

    except subprocess.TimeoutExpired:
        print(f"curl command for UID {uid} timed out")
        error_status = {"status": "Failed", "progress": 100, "details": "请求超时，请稍后重试"}
        redis_handler.set_job_status(job_id, error_status)
        return []
    except subprocess.CalledProcessError as e:
        print(f"curl command for UID {uid} failed: {e.stderr}")
        error_status = {"status": "Failed", "progress": 100, "details": f"网络请求失败: {e.stderr}"}
        redis_handler.set_job_status(job_id, error_status)
        return []
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON from curl for UID {uid}: {e}")
        error_status = {"status": "Failed", "progress": 100, "details": f"数据解析失败: {e}"}
        redis_handler.set_job_status(job_id, error_status)
        return []
    except Exception as e:
        print(f"An unexpected error occurred during comment fetching for UID {uid}: {e}")
        error_status = {"status": "Failed", "progress": 100, "details": f"获取评论时发生未知错误: {e}"}
        redis_handler.set_job_status(job_id, error_status)
        return []

    # 3. 将用户评论数据直接存储到Redis，键为uid
    try:
        # 存储原始评论数据到Redis，键为uid
        redis_handler.redis_insert(str(uid), user_comments)
        print(f"Stored {len(user_comments)} comments for UID {uid} in Redis cache")
    except Exception as e:
        print(f"Failed to store comments in Redis for UID {uid}: {e}")
        # 不中断流程，继续执行

    # 4. Update status: Completed
    print(f"Successfully processed job {job_id} for UID {uid}.")
    final_result = {
        "comments": user_comments,
        "comment_count": len(user_comments)
    }
    status_update = {
        "status": "Complete", 
        "progress": 100, 
        "details": f"用户 {uid} 评论获取完成，共获取 {len(user_comments)} 条评论",
        "result": final_result
    }
    redis_handler.set_job_status(job_id, status_update)

    return user_comments

async def user_select_simple_async(uid: int, job_id: str) -> Optional[List[Dict[str, Any]]]:
    """
    异步简化版用户评论获取函数，只获取评论数据并存储到Redis，不进行AI分析
    """


    # 1. Update status: Fetching comments
    status_update = {"status": "Processing", "progress": 40, "details": f"正在异步获取用户 {uid} 的评论..."}
    redis_handler.set_job_status(job_id, status_update)

    # 2. Fetch comments using aiohttp (async)
    try:
        api_url = f'https://api.aicu.cc/api/v3/search/getreply?uid={uid}&ps=100&pn=1&mode=0&keyword='
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }
        
        print(f"开始异步获取用户 {uid} 的评论...")
        
        # 使用aiohttp进行异步HTTP请求
        timeout = aiohttp.ClientTimeout(total=15, connect=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status != 200:
                    print(f"API请求失败，状态码: {response.status}")
                    error_status = {"status": "Failed", "progress": 100, "details": f"API请求失败，状态码: {response.status}"}
                    redis_handler.set_job_status(job_id, error_status)
                    return []
                
                json_str = await response.text()
                
                if not json_str.strip():
                    print(f"API返回空数据 for UID {uid}")
                    error_status = {"status": "Failed", "progress": 100, "details": "API返回空数据"}
                    redis_handler.set_job_status(job_id, error_status)
                    return []
                
                data = json.loads(json_str)
                replies = data.get('data', {}).get('replies', [])
                
                if not replies:
                    print(f"API returned no comments for UID {uid}")
                    no_data_status = {"status": "Complete", "progress": 100, "details": f"用户 {uid} 暂无评论数据"}
                    redis_handler.set_job_status(job_id, no_data_status)
                    return []
                
                user_comments = [{'comment_text': reply.get('message')} for reply in replies if reply.get('message')]
                print(f"成功获取 {len(user_comments)} 条评论 for UID {uid}")

    except asyncio.TimeoutError:
        print(f"aiohttp request for UID {uid} timed out")
        error_status = {"status": "Failed", "progress": 100, "details": "请求超时，请稍后重试"}
        redis_handler.set_job_status(job_id, error_status)
        return []
    except aiohttp.ClientError as e:
        print(f"aiohttp request for UID {uid} failed: {e}")
        error_status = {"status": "Failed", "progress": 100, "details": f"网络请求失败: {e}"}
        redis_handler.set_job_status(job_id, error_status)
        return []
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON for UID {uid}: {e}")
        error_status = {"status": "Failed", "progress": 100, "details": f"数据解析失败: {e}"}
        redis_handler.set_job_status(job_id, error_status)
        return []
    except Exception as e:
        print(f"An unexpected error occurred during comment fetching for UID {uid}: {e}")
        error_status = {"status": "Failed", "progress": 100, "details": f"获取评论时发生未知错误: {e}"}
        redis_handler.set_job_status(job_id, error_status)
        return []

    # 3. 将用户评论数据直接存储到Redis，键为uid
    try:
        # 存储原始评论数据到Redis，键为uid
        redis_handler.redis_insert(str(uid), user_comments)
        print(f"Stored {len(user_comments)} comments for UID {uid} in Redis cache")
    except Exception as e:
        print(f"Failed to store comments in Redis for UID {uid}: {e}")
        # 不中断流程，继续执行

    # 4. Update status: Completed
    print(f"Successfully processed job {job_id} for UID {uid}.")
    final_result = {
        "comments": user_comments,
        "comment_count": len(user_comments)
    }
    status_update = {
        "status": "Complete", 
        "progress": 100, 
        "details": f"用户 {uid} 评论获取完成，共获取 {len(user_comments)} 条评论",
        "result": final_result
    }
    redis_handler.set_job_status(job_id, status_update)

    return user_comments


def get_user_comments_simple(uid: int) -> List[Dict[str, Any]]:
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
        print(f"响应内容: {result.stdout[:200]}...")
        return []
    except Exception as e:
        print(f"获取评论时发生未知错误 for UID {uid}: {e}")
        return []

