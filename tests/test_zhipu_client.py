from zai import ZhipuAiClient

# 测试基本功能
def test_basic_function():
    client = ZhipuAiClient(api_key="34e734c4027a482898753aed0744527f.h721LazbYqHMfHNS")
    
    # 简单测试 - 使用正确格式
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
        ],
        max_tokens=65536,
        temperature=1.0
    )
    
    print("Basic test response:", response.choices[0].message)
    return response

def test_with_thinking():
    client = ZhipuAiClient(api_key="34e734c4027a482898753aed0744527f.h721LazbYqHMfHNS")
    
    # 测试带思考模式 - 使用正确格式
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
        ],
        thinking={
            "type": "enabled"
        },
        max_tokens=65536,
        temperature=1.0
    )
    
    print("Thinking mode test response:", response.choices[0].message)
    return response

def test_original_format():
    """测试原始格式 - 简单字符串格式"""
    client = ZhipuAiClient(api_key="34e734c4027a482898753aed0744527f.h721LazbYqHMfHNS")
    
    # 测试原始格式
    response = client.chat.completions.create(
        model="glm-4.6v-flash",
        messages=[
            {"role": "user", "content": "test,回复测试成功即可"}
        ],
        thinking={
            "type": "enabled"
        },
        max_tokens=65536,
        temperature=1.0
    )
    
    print("Original format test response:", response.choices[0].message)
    return response

if __name__ == "__main__":
    print("Testing basic function...")
    try:
        test_basic_function()
        print("Basic test passed")
    except Exception as e:
        print(f"Basic test failed: {e}")
    
    print("\nTesting with thinking mode...")
    try:
        test_with_thinking()
        print("Thinking mode test passed")
    except Exception as e:
        print(f"Thinking mode test failed: {e}")
    
    print("\nTesting original format...")
    try:
        test_original_format()
        print("Original format test passed")
    except Exception as e:
        print(f"Original format test failed: {e}")
