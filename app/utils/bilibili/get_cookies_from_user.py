from typing import Dict, Any, Optional
import httpx

async def generate_bilibili_qrcode() -> Dict[str, str]:
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
        async with httpx.AsyncClient() as requests:
            response = await requests.get(url, headers=headers, timeout=10)
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


async def poll_bilibili_login(qrcode_key: str) -> Dict[str, Any]:
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
        async with httpx.AsyncClient() as requests:
            response = await requests.get(url, headers=headers, timeout=10)
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
