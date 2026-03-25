from zai import ZhipuAiClient

def test_exact_format():
    """测试与成功示例完全相同的格式"""
    client = ZhipuAiClient(api_key="34e734c4027a482898753aed0744527f.h721LazbYqHMfHNS")
    
    # 使用与成功示例完全相同的格式，但只包含文本
    response = client.chat.completions.create(
        model="glm-4.6v-flash",
        messages=[
            {
                "content": [
                    {
                        "type": "text",
                        "text": "test,回复测试成功即可"
                    }
                ],
                "role": "user"
            }
        ],
        thinking={
            "type": "enabled"
        }
    )
    
    print("Exact format test response:", response.choices[0].message)
    return response

def test_simple_format():
    """测试简单格式 - 但包含thinking参数"""
    client = ZhipuAiClient(api_key="34e734c4027a482898753aed0744527f.h721LazbYqHMfHNS")
    
    # 简单格式
    response = client.chat.completions.create(
        model="glm-4.6v-flash",
        messages=[
            {"role": "user", "content": "test,回复测试成功即可"}
        ],
        thinking={
            "type": "enabled"
        }
    )
    
    print("Simple format test response:", response.choices[0].message)
    return response

def test_without_thinking():
    """测试不带thinking参数的格式"""
    client = ZhipuAiClient(api_key="34e734c4027a482898753aed0744527f.h721LazbYqHMfHNS")
    
    # 简单格式，不带thinking参数
    response = client.chat.completions.create(
        model="glm-4.6v-flash",
        messages=[
            {"role": "user", "content": "test,回复测试成功即可"}
        ]
    )
    
    print("Without thinking test response:", response.choices[0].message)
    return response

if __name__ == "__main__":
    print("Testing exact format...")
    try:
        test_exact_format()
        print("Exact format test passed")
    except Exception as e:
        print(f"Exact format test failed: {e}")
    
    print("\nTesting simple format with thinking...")
    try:
        test_simple_format()
        print("Simple format test passed")
    except Exception as e:
        print(f"Simple format test failed: {e}")
        
    print("\nTesting without thinking...")
    try:
        test_without_thinking()
        print("Without thinking test passed")
    except Exception as e:
        print(f"Without thinking test failed: {e}")
