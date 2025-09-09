#!/usr/bin/env python3
"""
测试异步评论获取功能
"""
import sys
import os
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), '../core'))

import bilibili
import time

async def test_async_comment_fetch():
    """测试异步评论获取功能"""
    print("开始测试异步评论获取功能...")
    
    # 测试UID
    test_uid = 66143532
    test_job_id = "test_async_job_" + str(int(time.time()))
    
    print(f"测试UID: {test_uid}")
    print(f"测试Job ID: {test_job_id}")
    
    try:
        print("开始异步获取评论...")
        start_time = time.time()
        
        result = await bilibili.user_select_simple_async(test_uid, test_job_id)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ 异步评论获取完成，耗时: {duration:.2f}秒")
        
        if result:
            print(f"✅ 成功获取 {len(result)} 条评论")
            # 显示前3条评论
            for i, comment in enumerate(result[:3]):
                print(f"  评论 {i+1}: {comment.get('comment_text', '')[:50]}...")
        else:
            print("⚠️ 未获取到评论数据")
            
        return True
        
    except Exception as e:
        print(f"❌ 异步评论获取失败: {e}")
        return False

async def test_multiple_async_fetch():
    """测试多个异步请求"""
    print("\n开始测试多个异步请求...")
    
    test_uids = [66143532, 34569411, 474791758]
    tasks = []
    
    for i, uid in enumerate(test_uids):
        job_id = f"test_multi_job_{i}_{int(time.time())}"
        task = bilibili.user_select_simple_async(uid, job_id)
        tasks.append(task)
    
    start_time = time.time()
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ 多个异步请求完成，总耗时: {duration:.2f}秒")
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"  请求 {i+1} (UID: {test_uids[i]}) 失败: {result}")
            else:
                print(f"  请求 {i+1} (UID: {test_uids[i]}) 成功: {len(result) if result else 0} 条评论") # type: ignore
        
        return True
        
    except Exception as e:
        print(f"❌ 多个异步请求失败: {e}")
        return False

async def main():
    """主函数"""
    print("=== 异步评论获取测试 ===")
    
    # 测试单个异步请求
    success1 = await test_async_comment_fetch()
    
    # 测试多个异步请求
    success2 = await test_multiple_async_fetch()
    
    if success1 and success2:
        print("\n🎉 所有异步测试通过！")
        return True
    else:
        print("\n💥 异步测试失败！")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 