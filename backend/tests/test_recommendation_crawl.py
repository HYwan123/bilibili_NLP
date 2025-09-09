#!/usr/bin/env python3
"""
测试推荐系统的爬取功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../core'))

from recommendation_model import get_sample_video_data
import json


def test_crawl_function():
    """
    测试爬取函数
    """
    print("=" * 50)
    print("测试B站视频数据爬取功能")
    print("=" * 50)
    
    try:
        # 调用爬取函数
        videos = get_sample_video_data()
        
        print(f"爬取结果: 共获取 {len(videos)} 个视频")
        print("-" * 30)
        
        # 显示前3个视频的详细信息
        for i, video in enumerate(videos[:3]):
            print(f"视频 {i+1}:")
            print(f"  ID: {video.get('video_id', 'N/A')}")
            print(f"  标题: {video.get('title', 'N/A')}")
            print(f"  分类: {video.get('category', 'N/A')}")
            print(f"  作者: {video.get('author', 'N/A')}")
            print(f"  播放量: {video.get('view_count', 0):,}")
            print(f"  时长: {video.get('duration', 'N/A')}")
            print(f"  发布时间: {video.get('pub_date', 'N/A')}")
            print(f"  描述: {video.get('description', 'N/A')[:100]}...")
            print(f"  关键词: {video.get('keyword', 'N/A')}")
            print()
        
        # 统计信息
        categories = {}
        total_views = 0
        
        for video in videos:
            category = video.get('category', '未知')
            categories[category] = categories.get(category, 0) + 1
            total_views += video.get('view_count', 0)
        
        print("统计信息:")
        print(f"  总播放量: {total_views:,}")
        print(f"  平均播放量: {total_views // len(videos) if videos else 0:,}")
        print("  分类分布:")
        for category, count in categories.items():
            print(f"    {category}: {count} 个视频")
        
        # 验证数据完整性
        print("\n数据完整性检查:")
        required_fields = ['video_id', 'title', 'category', 'description', 'view_count', 'pub_date']
        
        for field in required_fields:
            valid_count = sum(1 for video in videos if video.get(field))
            print(f"  {field}: {valid_count}/{len(videos)} 个视频有效")
        
        # 保存结果到文件
        with open('crawl_test_result.json', 'w', encoding='utf-8') as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到 crawl_test_result.json")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_crawl_function()
    if success:
        print("\n✅ 爬取功能测试成功!")
    else:
        print("\n❌ 爬取功能测试失败!")
