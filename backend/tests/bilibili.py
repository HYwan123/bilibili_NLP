import httpx
import json
import redis
import asyncio


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

async def get_comments(BV: str, page_many: int):
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
        async with httpx.AsyncClient() as request:
            request_output = await request.get(get_url(BV, page), headers = headers)
        request_output.encoding = 'utf-8'
        print(request_output.text)
        comments = json_load_2(request_output.text)

    return comments


def json_load_2(data_json: str):
    comments = []
    try:
        data = json.loads(data_json)
        if data.get('code') == 0:
            replies = data.get('data', {}).get('replies', [])
            
            # 确保 replies 是一个列表
            if not isinstance(replies, list):
                print(f"replies 不是列表类型: {type(replies)}")
                return comments
                
            for reply in replies:
                # 检查 reply 是否为字典类型
                if not isinstance(reply, dict):
                    continue
                    
                # 主评论
                main_comment = {
                    'user': reply.get('member', {}).get('uname', ''),
                    'content': reply.get('content', {}).get('message', ''),
                    'likes': reply.get('like', 0)
                }
                comments.append(main_comment)
                
                # 子回复 - 添加安全检查
                sub_replies = reply.get('replies')
                if sub_replies is not None and isinstance(sub_replies, list):
                    for sub_reply in sub_replies:
                        if isinstance(sub_reply, dict):
                            sub_comment = {
                                'user_name': sub_reply.get('member', {}).get('uname', ''),
                                'comment_text': sub_reply.get('content', {}).get('message', ''),
                                'bert_label': "待分析"
                            }
                            comments.append(sub_comment)
                            
    except (json.JSONDecodeError, AttributeError, TypeError) as e:
        print(f"解析评论数据时出错: {e}")
        import traceback
        traceback.print_exc()
    
    return comments


def json_load_1(data_json: str):
    comments = []
    text2json = json.loads(data_json)
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

async def main() -> None:
    bv = input()
    result = await get_comments(bv, 1)
    print(result)


if __name__ == '__main__':
    asyncio.run(main())