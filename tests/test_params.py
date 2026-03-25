from zai import ZhipuAiClient

def test_with_all_params():
    """测试包含所有参数的调用"""
    client = ZhipuAiClient(api_key="34e734c4027a482898753aed0744527f.h721LazbYqHMfHNS")
    
    # 测试包含所有参数
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
        },
        max_tokens=65536,
        temperature=1.0
    )
    
    print("All params test response:", response.choices[0].message)
    return response

def test_with_minimal_params():
    """测试最少参数的调用"""
    client = ZhipuAiClient(api_key="34e734c4027a482898753aed0744527f.h721LazbYqHMfHNS")
    
    # 测试最少参数
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
        ]
    )
    
    print("Minimal params test response:", response.choices[0].message)
    return response

def test_with_thinking_only():
    """测试只有thinking参数的调用"""
    client = ZhipuAiClient(api_key="34e734c4027a482898753aed0744527f.h721LazbYqHMfHNS")
    
    # 测试只有thinking参数
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
    
    print("Thinking only test response:", response.choices[0].message)
    return response

if __name__ == "__main__":
    print("Testing with all params...")
    try:
        test_with_all_params()
        print("All params test passed")
    except Exception as e:
        print(f"All params test failed: {e}")
    
    print("\nTesting with minimal params...")
    try:
        test_with_minimal_params()
        print("Minimal params test passed")
    except Exception as e:
        print(f"Minimal params test failed: {e}")
    
    print("\nTesting with thinking only...")
    try:
        test_with_thinking_only()
        print("Thinking only test passed")
    except Exception as e:
        print(f"Thinking only test failed: {e}")
