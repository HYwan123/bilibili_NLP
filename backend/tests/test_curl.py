#!/usr/bin/env python3
"""
测试修改后的get_user_comments_simple函数
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../core'))

from bilibili import get_user_comments_simple

def test_get_user_comments():
    uid = 66143532
    print(f"测试获取用户 {uid} 的评论...")
    
    comments = get_user_comments_simple(uid)
    
    if comments:
        print(f"成功获取 {len(comments)} 条评论")
        print("前3条评论:")
        for i, comment in enumerate(comments[:3]):
            print(f"{i+1}. {comment['comment_text']}")
    else:
        print("未获取到评论数据")

if __name__ == "__main__":
    test_get_user_comments() 