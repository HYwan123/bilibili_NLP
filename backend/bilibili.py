import requests
import json
from . import sql_use
from typing import List, Optional, Dict, Any
import subprocess
from . import vector_db
import os

def get_url(BV: str, page: int) -> str:
    url_base = ('https://api.bilibili.com/x/v2/reply/main?')
    url_page = (f'next={page}&type=1&')
    url_BV = (f'oid={BV}&mode=3')
    return url_base+url_page+url_BV

def get_comments(BV: str, page_many: int) -> list[dict]:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/xx.xx.xx.xx Safari/537.36',
        'Referer': f'https://www.bilibili.com/video/{BV}',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': "buvid3=22F3D67F-CD39-FF6A-7ADB-33AD9046131D92805infoc; b_nut=1723609892; _uuid=5210472E10-F387-9210E-1B22-E11734F8229591662infoc; enable_web_push=DISABLE; rpdid=|(JYYkYR)~m)0J'u~kJY|mm|~; buvid4=92701556-67AA-8ED4-2B50-61B34E41F4CC78670-023093020-wBy%2Br%2Fnp5uiSs%2BjLtOaZpQ%3D%3D; buvid_fp_plain=undefined; hit-dyn-v2=1; LIVE_BUVID=AUTO3517264644735245; is-2022-channel=1; DedeUserID=66143532; DedeUserID__ckMd5=71c2b65aa4ec6104; SESSDATA=b33bc351%2C1752329042%2Cc4d71%2A11CjBE8WxfW-PJf5Y1wosSGSl3LJ8uyWtCYscDS0t6i2sk0z7vnJ3wVU-dEYle2JzxdiQSVjVWWkRIX0tOd0M2eUR3dmhSdnZObzlqMWhKelIySHpTYXVUcFJBRXN4Z0hna0Jfam4zUW1sQ0J4ZHkxTEpja0RGWWhrMGhSSEdBVnlGbE44SHA5MFNBIIEC; bili_jct=872ea96c57ed1e5f46c12b685c1f6dbd; enable_feed_channel=ENABLE; header_theme_version=OPEN; theme-tip-show=SHOWED; theme-avatar-tip-show=SHOWED; CURRENT_QUALITY=120; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDk5ODU3NjYsImlhdCI6MTc0OTcyNjUwNiwicGx0IjotMX0.4SmgtVyrkjAnxLbJFXcuRLnOhO3E0vdKa5u_VujC6OQ; bili_ticket_expires=1749985706; home_feed_column=5; b_lsid=45E46954_1976E1B5F4D; fingerprint=656ce9aa7b0b83bb03761b98efd43ea9; sid=8qeu1cpx; browser_resolution=2552-1330; bp_t_offset_66143532=1078307369940680704; buvid_fp=656ce9aa7b0b83bb03761b98efd43ea9; PVID=2; CURRENT_FNVAL=4048"
    }
    comments = []
    for page in range(page_many):
        request_output = requests.get(get_url(BV, page), headers = headers)
        request_output.encoding = 'utf-8'
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
    """
    Fetches user comments via an external API using curl, stores them, 
    performs vector analysis, and updates job status in Redis.
    """
    redis_handler = sql_use.SQL_redis()

    # 1. Update status: Fetching comments
    status_update = {"status": "Processing", "progress": 40, "details": f"正在通过cURL获取用户 {uid} 的评论..."}
    redis_handler.set_job_status(job_id, status_update)

    # 2. Fetch comments using curl via subprocess
    try:
        api_url = f'https://api.aicu.cc/api/v3/search/getreply?uid={uid}&ps=100&pn=1&mode=0&keyword='
        # Using a list of arguments is safer. Add a User-Agent header to mimic a browser.
        command = [
            'curl',
            '-s', # Silent mode
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

    # 3. Update status: Processing and storing vectors
    status_update = {"status": "Processing", "progress": 70, "details": "获取评论成功，正在进行AI分析和存储..."}
    redis_handler.set_job_status(job_id, status_update)
    
    # 4. Perform vector analysis and storage
    try:
        # Step 4a: Process texts, embed, and store in Milvus. This is the correct function name.
        vector_db.process_and_store_comments(uid, user_comments)
        
        # Step 4b: Calculate the average vector after storing.
        avg_vector = vector_db.get_user_avg_vector(uid)
        avg_vector_list = avg_vector.tolist() if avg_vector.size > 0 else []

    except Exception as e:
        print(f"Vector analysis for UID {uid} failed: {e}")
        # Update status to Failed
        error_message = f"AI分析或向量存储失败: {e}"
        status_update = {"status": "Failed", "progress": 100, "details": error_message}
        redis_handler.set_job_status(job_id, status_update)
        raise Exception(error_message)

    # 5. Update status: Completed
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

def select_by_BV(BV: str) -> List[dict]:
    """
    Selects comments for a given Bilibili video BV ID.
    First, it checks for cached data in Redis. If not found,
    it fetches the comments, caches them, and then returns them.
    """
    sql_redis_handler = sql_use.SQL_redis()
    
    # 1. Check cache first
    cached_data = sql_redis_handler.redis_select(BV)
    if cached_data:
        print(f"Cache hit for BV: {BV}")
        return cached_data

    # 2. If cache miss, fetch from source
    print(f"Cache miss for BV: {BV}. Fetching from source.")
    new_comments = get_comments(BV, 1)  # Fetch first page of comments

    # 3. Store in cache if data is fetched
    if new_comments:
        print(f"Storing {len(new_comments)} new comments for BV: {BV} in cache.")
        sql_redis_handler.redis_insert(BV, new_comments)
        return new_comments
    else:
        print(f"Failed to fetch comments for BV: {BV}")
        return []

def main():
    user_select(474791758)

if __name__ == "__main__":
    main()

def select_bilibili(BV: str) -> List:
    if result := sql_use.redis_select('BV1cGEJzQEvV') is None:
        sql_use.redis_insert('BV1cGEJzQEvV', get_comments('BV1cGEJzQEvV', 1))
    result = sql_use.redis_select('BV1cGEJzQEvV')
    return result

def insert_bilibili(BV: str) -> bool:
    pass

def main():
    user_select(1)

if __name__ == '__main__':
    main()