from zai import ZhipuAiClient

def test_basic_call():
    """测试基础调用"""
    client = ZhipuAiClient(api_key="34e734c4027a482898753aed0744527f.h721LazbYqHMfHNS")
    
    # 完全按照成功示例的格式
    response = client.chat.completions.create(
        model="glm-4.6v-flash",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "test,回复测试成功即可"
                    }
                ]
            }
        ]
    )
    
    print("Basic call response:", response.choices[0].message)
    return response

def test_with_system_prompt():
    """测试带系统提示词的调用"""
    client = ZhipuAiClient(api_key="34e734c4027a482898753aed0744527f.h721LazbYqHMfHNS")
    
    # 带系统提示词的调用
    response = client.chat.completions.create(
        model="glm-4.6v-flash",
        messages=[
            {
                "role": "system",
                "content": "你是一个有用的助手"
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "test,回复测试成功即可"
                    }
                ]
            }
        ],
        thinking={
            "type": "enabled"
        }
    )
    
    print("With system prompt response:", response.choices[0].message)
    return response

if __name__ == "__main__":
    print("Testing basic call...")
    try:
        test_basic_call()
        print("Basic call test passed")
    except Exception as e:
        print(f"Basic call test failed: {e}")
    
    print("\nTesting with system prompt...")
    try:
        test_with_system_prompt()
        print("System prompt test passed")
    except Exception as e:
        print(f"System prompt test failed: {e}")
