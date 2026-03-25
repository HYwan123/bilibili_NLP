import asyncio
from app.utils.agent.openai_client import OpenaiClient

async def test_one_chat():
    client = OpenaiClient()
    
    # 测试 one_chat 方法
    result = await client.one_chat("test,回复测试成功即可")
    print("one_chat result:", type(result))
    if hasattr(result, 'choices'):
        print("Content:", client.get_message_content(result))
    else:
        print("Response object does not have expected structure for getting content")

if __name__ == "__main__":
    asyncio.run(test_one_chat())
