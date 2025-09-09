import requests
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../core'))
import sql_use as sql_use

r = sql_use.SQL_redis().get_client()

def main() -> None:
    cookie = r.get('video_select_cookie') # type: ignore
    
    print(cookie)
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cookie': cookie
        }
    keyword = "wan"
    search_url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={keyword}&page=1&page_size=20"
    response = requests.get(search_url, headers=headers, timeout=10)
    print(response)
    data = response.json()
    print(data)
    
if __name__ == '__main__':
    main()