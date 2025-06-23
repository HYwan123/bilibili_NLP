#!/usr/bin/env python3
"""
测试API脚本
"""
import requests
import json

def test_api():
    base_url = "http://localhost:5480"
    
    # 1. 测试注册
    print("1. 测试注册...")
    register_data = {
        "username": "testuser2",
        "password": "test123"
    }
    
    try:
        register_response = requests.post(f"{base_url}/user/register", json=register_data)
        print(f"注册状态码: {register_response.status_code}")
        print(f"注册结果: {register_response.text}")
        
        # 2. 测试登录
        print("\n2. 测试登录...")
        login_data = {
            "username": "testuser2",
            "password": "test123"
        }
        
        login_response = requests.post(f"{base_url}/user/login", json=login_data)
        print(f"登录状态码: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"登录成功: {login_result}")
            token = login_result.get('data', {}).get('token')
            
            if token:
                print(f"获取到token: {token[:20]}...")
                
                # 3. 测试获取用户评论
                print("\n3. 测试获取用户评论...")
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                uid = 66143532
                comment_response = requests.post(f"{base_url}/api/user/comments/{uid}", headers=headers)
                print(f"获取评论状态码: {comment_response.status_code}")
                
                if comment_response.status_code == 200:
                    comment_result = comment_response.json()
                    print(f"获取评论成功: {comment_result}")
                else:
                    print(f"获取评论失败: {comment_response.text}")
                    
            else:
                print("未获取到token")
        else:
            print(f"登录失败: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("无法连接到后端服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")

if __name__ == "__main__":
    test_api() 