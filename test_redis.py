#!/usr/bin/env python3
"""
测试Redis连接和基本功能
"""
import redis
import json
import sys

def test_redis_connection():
    """测试Redis连接"""
    try:
        # 创建Redis连接
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # 测试连接
        r.ping()
        print("✅ Redis连接成功")
        
        # 测试基本操作
        test_key = "test_connection"
        test_value = {"status": "test", "message": "Hello Redis"}
        
        # 设置值
        r.set(test_key, json.dumps(test_value), ex=60)  # 60秒过期
        print("✅ 设置测试值成功")
        
        # 获取值
        result = r.get(test_key)
        if result:
            parsed_result = json.loads(result)
            print(f"✅ 获取测试值成功: {parsed_result}")
        else:
            print("❌ 获取测试值失败")
            return False
        
        # 测试列表操作
        test_queue = "test_queue"
        test_message = {"uid": 123, "job_id": "test-job-123"}
        
        # 推送到队列
        r.lpush(test_queue, json.dumps(test_message))
        print("✅ 推送到队列成功")
        
        # 从队列弹出
        queue_result = r.brpop(test_queue, 1)
        if queue_result:
            source, message = queue_result
            parsed_message = json.loads(message)
            print(f"✅ 从队列弹出成功: {parsed_message}")
        else:
            print("❌ 从队列弹出失败")
            return False
        
        # 清理测试数据
        r.delete(test_key)
        print("✅ 清理测试数据成功")
        
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Redis连接失败: {e}")
        print("请确保Redis服务正在运行: sudo systemctl start redis")
        return False
    except Exception as e:
        print(f"❌ Redis测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试Redis连接...")
    success = test_redis_connection()
    if success:
        print("\n🎉 Redis测试全部通过！")
        sys.exit(0)
    else:
        print("\n💥 Redis测试失败！")
        sys.exit(1) 