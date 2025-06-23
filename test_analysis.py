#!/usr/bin/env python3
"""
测试大模型API分析功能
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from bilibili import analyze_user_comments, get_user_comments_from_redis

def test_analysis():
    uid = 66143532
    print(f"测试用户 {uid} 的画像分析...")
    
    # 1. 先检查Redis中是否有评论数据
    comments = get_user_comments_from_redis(uid)
    if not comments:
        print("Redis中没有找到评论数据，请先获取评论")
        return
    
    print(f"找到 {len(comments)} 条评论")
    
    # 2. 进行画像分析
    result = analyze_user_comments(uid)
    
    if "error" in result:
        print(f"分析失败: {result['error']}")
    else:
        print("分析成功!")
        print(f"用户UID: {result['uid']}")
        print(f"评论数量: {result['comment_count']}")
        print(f"分析时间: {result['timestamp']}")
        print("\n分析内容:")
        print(result['analysis'])

if __name__ == "__main__":
    test_analysis() 