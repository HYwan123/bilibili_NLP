from zai import ZhipuAiClient

def test_simple_with_params():
    """测试简单调用但包含参数"""
    client = ZhipuAiClient(api_key="34e734c4027a482898753aed0744527f.h721LazbYqHMfHNS")
    
    # 测试包含max_tokens和temperature参数
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
    
    print("Simple with params response:", response.choices[0].message)
    return response

def test_with_thinking_and_params():
    """测试带有thinking和参数的调用"""
    client = ZhipuAiClient(api_key="34e734c4027a482898753aed0744527f.h721LazbYqHMfHNS")
    
    # 测试包含thinking和参数
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
    
    print("Thinking and params response:", response.choices[0].message)
    return response

if __name__ == "__main__":
    print("Testing simple with params...")
    try:
        test_simple_with_params()
        print("Simple with params test passed")
    except Exception as e:
        print(f"Simple with params test failed: {e}")
    
    print("\nTesting with thinking and params...")
    try:
        test_with_thinking_and_params()
        print("Thinking and params test passed")
    except Exception as e:
        print(f"Thinking and params test failed: {e}")
