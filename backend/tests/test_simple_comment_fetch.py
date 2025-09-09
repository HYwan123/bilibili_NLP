#!/usr/bin/env python3
"""
测试简单评论获取功能
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../core'))

import bilibili
import database
import time

def test_simple_comment_fetch():
    """测试简单评论获取功能"""
    print("开始测试简单评论获取功能...")
    
    # 测试UID
    test_uid = 66143532
    test_username = "test_user"
    
    print(f"测试UID: {test_uid}")
    print(f"测试用户名: {test_username}")
    
    try:
        print("开始获取评论...")
        start_time = time.time()
        
        # 获取评论
        comments = bilibili.get_user_comments_simple(test_uid)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ 评论获取完成，耗时: {duration:.2f}秒")
        
        if comments:
            print(f"✅ 成功获取 {len(comments)} 条评论")
            
            # 保存到数据库
            print("开始保存到数据库...")
            save_success = database.save_user_comments(test_uid, test_username, comments)
            
            if save_success:
                print("✅ 成功保存到数据库")
                
                # 从数据库读取
                print("开始从数据库读取...")
                saved_comments = database.get_user_comments(test_uid)
                
                if saved_comments:
                    print(f"✅ 成功从数据库读取 {len(saved_comments)} 条评论")
                    
                    # 显示前3条评论
                    for i, comment in enumerate(saved_comments[:3]):
                        print(f"  评论 {i+1}: {comment.get('comment_text', '')[:50]}...")
                else:
                    print("❌ 从数据库读取失败")
            else:
                print("❌ 保存到数据库失败")
        else:
            print("⚠️ 未获取到评论数据")
            
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_comment_fetch()
    if success:
        print("\n🎉 简单评论获取测试通过！")
        sys.exit(0)
    else:
        print("\n💥 简单评论获取测试失败！")
        sys.exit(1) 