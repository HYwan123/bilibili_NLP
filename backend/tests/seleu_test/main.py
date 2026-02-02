from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium_stealth import stealth
import json
import time

# --- 配置 ---
from selenium import webdriver
# ... (其他导入保持不变)

# --- 配置 ---
CHROMEDRIVER_PATH = './chromedriver' # 请确保路径正确且版本匹配
TARGET_URL = "https://api.aicu.cc/api/v3/search/getreply?uid=40082666&pn=1&ps=100&mode=0&keyword="

print("🚀 正在启动自动化浏览器 (Stealth Mode + Performance Log)...")
service = Service(executable_path=CHROMEDRIVER_PATH)
options = webdriver.ChromeOptions()

# *** 关键修改：将日志配置添加到 options 中 ***
options.set_capability("goog:loggingPrefs", {'performance': 'ALL'}) 
# **********************************************

# 反检测设置
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled') 
custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
options.add_argument(f"user-agent={custom_user_agent}")
options.add_argument('--headless=new')
# 驱动初始化不再需要 desired_capabilities 参数
driver = webdriver.Chrome(service=service, options=options)

# 2. 激活 Stealth 模式
stealth(driver,
        languages=["zh-CN", "zh"],
        vendor="Google Inc.",
        platform="Linux", # 尝试切换到 Linux
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
try:
    # 3. 访问目标 URL 并等待 WAF 挑战完成
    driver.get(TARGET_URL)
    print("⏳ 浏览器正在尝试绕过雷池 WAF 并等待 API 响应...")

    # 等待 API 响应出现在网络日志中
    WebDriverWait(driver, 45).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body')),
        message="页面加载超时"
    )
    
    # 额外等待，确保挑战和数据加载完毕
    time.sleep(10)
    
    print("✅ 挑战和加载完成。正在从浏览器日志中提取 API 数据...")
    
    # 4. 从 Performance Logs 中捕获 API 响应
    api_response_body = None
    for log_entry in driver.get_log('performance'):
        message = json.loads(log_entry['message'])
        message_data = message['message']['params']
        
        # 查找网络请求，特别是针对我们的 base_url 的请求
        if 'response' in message_data and message_data['response']['url'].startswith("https://api.aicu.cc/api/v3/search/getreply"):
            request_id = message_data['requestId']
            
            # 使用 DevTools Protocol 获取响应体
            try:
                response_body_data = driver.execute_cdp_cmd(
                    'Network.getResponseBody', {'requestId': request_id}
                )
                api_response_body = response_body_data['body']
                print("🎉 成功！已从浏览器内部获取到响应体。")
                break
            except Exception as e:
                # print(f"无法获取响应体: {e}")
                pass
    
    # 5. 处理结果
    if api_response_body:
        # 尝试解析 JSON 数据
        try:
            data = json.loads(api_response_body)
            print("--- API 返回数据 (前 500 字符) ---")
            print(json.dumps(data, indent=4, ensure_ascii=False)[:500] + "...")
        except json.JSONDecodeError:
            print("❌ 警告：获取的响应不是有效的 JSON 格式，可能是 WAF 拦截页面。")
            print("部分响应内容:", api_response_body[:500])
    else:
        print("❌ 最终请求失败。未能在浏览器日志中捕获到成功的 API 响应。")
        print("当前页面标题:", driver.title)

except Exception as e:
    print(f"❌ 发生异常: {e}")
finally:
    driver.quit()
    print("浏览器已关闭。")