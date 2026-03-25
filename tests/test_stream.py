import asyncio
from app.utils.agent.openai_client import OpenaiClient

async def test_stream():
    client = OpenaiClient()
    
    # 测试 chat_stream 方法
    print("Testing stream with no system prompt:")
    async for chunk in client.chat_stream([{"role": "user", "content": "test,回复测试成功即可"}]):
        print(chunk, end='', flush=True)
    print()
    


if __name__ == "__main__":
    asyncio.run(test_stream())
