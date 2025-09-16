import requests
from core import sql_use

redis = sql_use.SQL_redis()

def get_video_info(BVid: str) -> dict:
    cookie = redis.redis_select_by_key('cookie_video_info')
    url = f'https://api.bilibili.com/x/tag/archive/tags?bvid={BVid}'
    headers = {
        'Cookie': cookie
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        title = data['data'].get('title', '')
        desc = data['data'].get('desc', '')
        tag_primary = data['data'].get('tname', '')
        tag_secondary = data['data'].get('tname_v2', '')
        return {'msg': 'OK', 'title': title, 'desc': desc, 'tag_primary': tag_primary, 'tag_secondary': tag_secondary}
    else:
        return {'msg': 'fail'}
    
def get_video_tags(BVid: str) -> list[str]:
    cookie = redis.redis_select_by_key('cookie_video_tages') 
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Cookie": cookie
    }
    json_data = requests.get(url=f'https://api.bilibili.com/x/tag/archive/tags?bvid={BVid}', headers=headers).json()
    tags = [tag["tag_name"] for tag in json_data["data"]]
    return tags