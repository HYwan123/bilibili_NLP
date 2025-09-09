#!/usr/bin/env python3
"""
测试评论获取功能
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../core'))

# 修改导入方式
import bilibili
import time

def test_comment_fetch():
    """测试评论获取功能"""
    print("开始测试评论获取功能...")
    
    # 测试UID
    test_uid = 66143532
    test_job_id = "test_job_" + str(int(time.time()))
    
    print(f"测试UID: {test_uid}")
    print(f"测试Job ID: {test_job_id}")
    
    try:
        print("开始获取评论...")
        start_time = time.time()
        
        result = bilibili.user_select_simple(test_uid, test_job_id)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ 评论获取完成，耗时: {duration:.2f}秒")
        
        if result:
            print(f"✅ 成功获取 {len(result)} 条评论")
            # 显示前3条评论
            for i, comment in enumerate(result[:3]):
                print(f"  评论 {i+1}: {comment.get('comment_text', '')[:50]}...")
        else:
            print("⚠️ 未获取到评论数据")
            
        return True
        
    except Exception as e:
        print(f"❌ 评论获取失败: {e}")
        return False

if __name__ == "__main__":
    success = test_comment_fetch()
    if success:
        print("\n🎉 测试通过！")
        sys.exit(0)
    else:
        print("\n💥 测试失败！")
        sys.exit(1) 