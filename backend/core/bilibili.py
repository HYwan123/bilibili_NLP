import httpx
import requests
import json
import core.sql_use as sql_use
from typing import List, Optional, Dict, Any
import subprocess
import aiohttp
import asyncio
import redis
from datetime import datetime
import core.database as database_mysql

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def lpush(uid: int) -> bool:
    redis_client.lpush('uids', uid)
    return True

def get_url(BV: str, page: int) -> str:
    url_base = ('https://api.bilibili.com/x/v2/reply/main?')
    url_page = (f'next={page}&type=1&')
    url_BV = (f'oid={BV}&mode=3&ps=20')
    return url_base+url_page+url_BV

def get_cookie() -> str:
    return redis_client.get('cookie') # type: ignore

def set_cookie(cookie: str) -> None:
    redis_client.set('cookie', cookie)

def get_comments(BV: str, page_many: int) -> list[dict]:
    try:
        cookie = get_cookie()
        print(cookie)
    except:
        cookie = "buvid3=44209DC6-8F36-21E9-E2DD-293916C709B523950infoc; b_nut=1756613223; _uuid=68AB106DE-B678-F26C-B1F9-97947CA5ED6266013infoc; enable_web_push=DISABLE; buvid4=785B80FE-5720-9135-61F3-62A87F54713024946-025083112-gbmnyNGGAgQhJoYQQQoq2A%3D%3D; bili_jct=986fbe7483bb350ca6b1e8a5564347ab; DedeUserID=66143532; DedeUserID__ckMd5=71c2b65aa4ec6104; theme-tip-show=SHOWED; theme-avatar-tip-show=SHOWED; theme-switch-show=SHOWED; theme_style=dark; hit-dyn-v2=1; rpdid=|(um~kJRmkl)0J'u~lYYRlRYm; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTcwNzQzOTQsImlhdCI6MTc1NjgxNTEzNCwicGx0IjotMX0.HTMOpZSE4oDOH3TM3KP2vyuClhY80DxOSPtwSbSwXIY; bili_ticket_expires=1757074334; CURRENT_QUALITY=116; fingerprint=c538929c04b4400b1cc8cd12b5f1597b; buvid_fp_plain=undefined; buvid_fp=c538929c04b4400b1cc8cd12b5f1597b; bp_t_offset_66143532=1108380039457538048; b_lsid=437B19E9_19911FE1E25; bmg_af_switch=1; bmg_src_def_domain=i0.hdslb.com; bsource=search_google; sid=579q033f; CURRENT_FNVAL=4048; home_feed_column=5; browser_resolution=1412-985"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Referer': f'https://www.bilibili.com/video/{BV}',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': cookie
        }
    comments = []
    for page in range(page_many):
        request_output = requests.get(get_url(BV, page), headers = headers)
        request_output.encoding = 'utf-8'
        print(request_output.text)
        text2json = json.loads(request_output.text)
        if text2json['message'] == '0':
            if text2json['data']['replies']:
                for i in range(len(text2json['data']['replies'])):
                    comment_info = {
                        "user_name": text2json['data']['replies'][i]['member']['uname'],
                        "comment_text": text2json['data']['replies'][i]['content']['message'],
                        "bert_label": "待分析"
                    }
                    comments.append(comment_info)
    
        else:
            return [] # 返回空列表表示未获取到
    return comments

def user_select(uid: int, job_id: str) -> Optional[List[Dict[str, Any]]]:
    redis_handler = sql_use.SQL_redis()
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
    redis_handler = sql_use.SQL_redis()

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
    redis_handler = sql_use.SQL_redis()

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

def select_by_BV(BV: str) -> List[dict]:
    """
    根据指定的 Bilibili 视频 BV 号获取评论。
    函数会先检查 Redis 中是否有缓存数据；
    如果有，则直接返回缓存数据；
    如果没有，则从源接口获取评论，并写入缓存，再返回结果。
    """
    sql_redis_handler = sql_use.SQL_redis()
    # 1. 先检查缓存
    cached_data = sql_redis_handler.redis_select(BV)
    if cached_data:
        print(f"Cache hit for BV: {BV}")
        return cached_data

    # 2. 如果缓存未命中，则从源获取
    print(f"Cache miss for BV: {BV}. Fetching from source.")
    new_comments = get_comments(BV, 10)  # Fetch first page of comments

    # 3. 如果获取到了评论，就写入缓存
    if new_comments:
        print(f"Storing {len(new_comments)} new comments for BV: {BV} in cache.")
        sql_redis_handler.redis_insert(BV, new_comments)
        return new_comments
    else:
        print(f"Failed to fetch comments for BV: {BV}")
        return []

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
        redis_client.set(str(uid), json.dumps(user_comments, ensure_ascii=False))
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

async def analyze_user_comments(uid: int) -> Dict[str, Any]:
    """
    使用大模型API分析用户评论，生成用户画像
    """
    print("调用分析画像函数")
    if redis_client.exists(f"analysis_{uid}"):
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
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(api_url, headers=headers, json=data)
        
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


def generate_bilibili_qrcode() -> Dict[str, str]:
    """
    Generate Bilibili QR code for login
    Returns: dict with 'qrcode_key' and 'url'
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
    }

    url = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate?source=main-fe-header&go_url=https:%2F%2Fwww.bilibili.com%2F%3Fspm_id_from%3D333.1387.0.0&web_location=333.1007"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('code') != 0:
            raise Exception(f"生成二维码失败: {data.get('message', '未知错误')}")

        return {
            'qrcode_key': data['data']['qrcode_key'],
            'url': data['data']['url']
        }
    except Exception as e:
        print(f"生成Bilibili二维码失败: {e}")
        raise Exception(f"生成二维码失败: {str(e)}")


def poll_bilibili_login(qrcode_key: str) -> Dict[str, Any]:
    """
    Poll Bilibili login status
    Returns: dict with login status information
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
    }

    url = f"https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={qrcode_key}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Bilibili returns the login status in data.data.code:
        # 0 = success, 86101 = not scanned yet, 86090 = scanned, 86038 = expired
        return {
            'code': data.get('code', -1),  # Overall API call success/failure
            'message': data.get('message', ''),
            'data': {
                'code': data.get('data', {}).get('code', -1),  # Login status
                'message': data.get('data', {}).get('message', ''),
                'url': data.get('data', {}).get('url', ''),
                'refresh_token': data.get('data', {}).get('refresh_token', ''),
                'timestamp': data.get('data', {}).get('timestamp', '')
            }
        }
    except Exception as e:
        print(f"轮询Bilibili登录状态失败: {e}")
        raise Exception(f"轮询登录状态失败: {str(e)}")


def extract_sessdata_from_url(url: str) -> Optional[Dict[str, str]]:
    """
    Extract SESSDATA and bili_jct from Bilibili login URL
    Returns: dict with 'sessdata' and 'bili_jct' or None if not found
    """
    try:
        from urllib.parse import urlparse, parse_qs

        # Parse URL parameters
        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)

        # Try to extract from URL parameters
        sessdata = params.get('SESSDATA', [None])[0]
        bili_jct = params.get('bili_jct', [None])[0]

        if sessdata and bili_jct:
            return {'sessdata': sessdata, 'bili_jct': bili_jct}

        # If not in URL parameters, try from fragment
        if parsed_url.fragment:
            fragment_params = parse_qs(parsed_url.fragment)
            hash_sessdata = fragment_params.get('SESSDATA', [None])[0]
            hash_bili_jct = fragment_params.get('bili_jct', [None])[0]

            if hash_sessdata and hash_bili_jct:
                return {'sessdata': hash_sessdata, 'bili_jct': hash_bili_jct}

        return None
    except Exception as e:
        print(f"解析登录URL失败: {e}")
        return None


def main():
    """测试函数"""
    user_select(474791758, "test_job_id")

if __name__ == "__main__":
    main()