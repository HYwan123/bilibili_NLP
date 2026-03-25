from app.utils.agent.openai_client import OpenaiClient
import asyncio

async def test_zhipu_client():
    print("测试 Zhipu AI 客户端...")
    client = OpenaiClient()
    
    # 测试同步聊天
    print("测试同步聊天:")
    response = await client.chat(
        messages=[{"role": "user", "content": "你好，这是一条测试消息"}],
        model="glm-4.7-flash"
    )
    print("同步聊天响应:", response)
    print("消息内容:", client.get_message_content(response))
    print("")
    
    # 测试流式聊天
    print("测试流式聊天:")
    print("流式输出: ", end="")
    async for chunk in client.chat_stream(
        messages=[{"role": "user", "content": "请简单介绍一下你自己"}],
        model="glm-4.7-flash"
    ):
        print(chunk, end="")
    print("\n")
    
    # 测试单次聊天
    print("测试单次聊天:")
    response = await client.one_chat("今天天气怎么样？", model="glm-4.7-flash")
    print("单次聊天响应:", response)
    print("消息内容:", client.get_message_content(response))
    
    print("测试完成！")

if __name__ == "__main__":
    asyncio.run(test_zhipu_client())
