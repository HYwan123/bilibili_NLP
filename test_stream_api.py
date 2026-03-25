import asyncio
import json
from app.utils.agent.openai_client import OpenaiClient
import httpx


async def test_stream_client():
    """测试流式客户端"""
    print("开始测试流式客户端...")
    client = OpenaiClient()
    
    messages = [
        {"role": "user", "content": "你好，请简单介绍一下人工智能，只需要一句话。"}
    ]
    
    try:
        chunk_count = 0
        full_response = ""
        async for content in client.chat_stream(
            messages=messages,
            model="glm-4.7-flash",
            system_prompt="你是一个有用的助手。"
        ):
            if content:
                chunk_count += 1
                full_response += content
                print(f"收到第{chunk_count}个片段: {content}")
        
        print(f"流式客户端测试完成，共收到{chunk_count}个片段")
        print(f"完整响应: {full_response}")
        return True
    except Exception as e:
        print(f"流式客户端测试失败: {e}")
        return False


def test_stream_endpoint():
    """测试流式API端点"""
    print("\n开始测试流式API端点...")
    
    # 创建请求数据
    data = {
        "messages": [
            {"role": "user", "content": "你好，请简单介绍一下机器学习，只需要一句话。"}
        ],
        "model": "glm-4.7-flash"
    }
    
    try:
        with httpx.stream(
            "POST", 
            "http://127.0.0.1:8000/api/bilibili/chat/stream", 
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30.0
        ) as response:
            if response.status_code == 200:
                print("成功连接到流式API端点")
                chunk_count = 0
                full_response = ""
                
                # 手动解析SSE流
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        event_data = line[6:]  # 移除 "data: " 前缀
                        if event_data and event_data != "[DONE]":
                            try:
                                chunk_data = json.loads(event_data)
                                if "content" in chunk_data and chunk_data["content"]:
                                    chunk_count += 1
                                    content = chunk_data["content"]
                                    full_response += content
                                    print(f"收到第{chunk_count}个片段: {content}")
                            except json.JSONDecodeError:
                                print(f"无法解析数据: {event_data}")
                
                print(f"流式API端点测试完成，共收到{chunk_count}个片段")
                print(f"完整响应: {full_response}")
                return True
            else:
                print(f"API端点返回错误状态码: {response.status_code}")
                return False
    except Exception as e:
        print(f"流式API端点测试失败: {e}")
        return False


async def main():
    print("开始验证流式API修复...")
    
    # 测试客户端
    client_success = await test_stream_client()
    
    # 测试端点
    endpoint_success = test_stream_endpoint()
    
    print(f"\n测试结果:")
    print(f"客户端测试: {'通过' if client_success else '失败'}")
    print(f"端点测试: {'通过' if endpoint_success else '失败'}")
    
    if client_success and endpoint_success:
        print("\n所有测试通过！流式API修复成功。")
    else:
        print("\n部分测试失败，请检查API实现。")


if __name__ == "__main__":
    asyncio.run(main())
