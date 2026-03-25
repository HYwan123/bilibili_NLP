from zai import ZhipuAiClient

def test_params_with_model():
    """测试特定模型参数"""
    client = ZhipuAiClient(api_key="34e734c4027a482898753aed0744527f.h721LazbYqHMfHNS")
    
    # 测试不使用max_tokens和temperature参数
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
    
    print("Model params test response:", response.choices[0].message)
    return response

def test_params_with_thinking_only():
    """测试只使用thinking参数"""
    client = ZhipuAiClient(api_key="34e734c4027a482898753aed0744527f.h721LazbYqHMfHNS")
    
    # 测试只使用thinking参数，不使用max_tokens和temperature
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
        }
    )
    
    print("Thinking only test response:", response.choices[0].message)
    return response

if __name__ == "__main__":
    print("Testing model params...")
    try:
        test_params_with_model()
        print("Model params test passed")
    except Exception as e:
        print(f"Model params test failed: {e}")
    
    print("\nTesting thinking only...")
    try:
        test_params_with_thinking_only()
        print("Thinking only test passed")
    except Exception as e:
        print(f"Thinking only test failed: {e}")
