#!/usr/bin/env python3
"""
评论分析功能测试脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from bilibili import select_by_BV
from comment_analysis import analyze_bv_comments, get_bv_analysis

def test_comment_analysis():
    """测试评论分析功能"""
    
    # 测试BV ID（使用一个热门视频的BV号）
    test_bv = "BV1xx411c7mD"  # 可以替换为其他BV号
    
    print(f"开始测试评论分析功能...")
    print(f"测试BV: {test_bv}")
    
    try:
        # 1. 获取评论数据
        print("\n1. 获取评论数据...")
        comments = select_by_BV(test_bv)
        
        if not comments:
            print("未获取到评论数据，请检查BV号是否正确")
            return
        
        print(f"成功获取 {len(comments)} 条评论")
        
        # 2. 进行评论分析
        print("\n2. 进行评论分析...")
        analysis_result = analyze_bv_comments(test_bv, comments)
        
        if "error" in analysis_result:
            print(f"分析失败: {analysis_result['error']}")
            return
        
        print("评论分析完成！")
        
        # 3. 显示分析结果摘要
        print("\n3. 分析结果摘要:")
        print(f"   - 总评论数: {analysis_result['basic_stats']['total_comments']}")
        print(f"   - 独立用户数: {analysis_result['basic_stats']['unique_users']}")
        print(f"   - 平均评论长度: {analysis_result['basic_stats']['average_length']}")
        print(f"   - 平均质量评分: {analysis_result['content_quality']['average_quality_score']}")
        
        if 'sentiment_analysis' in analysis_result and 'overall_sentiment' in analysis_result['sentiment_analysis']:
            sentiment = analysis_result['sentiment_analysis']['overall_sentiment']
            print(f"   - 整体情感倾向: {sentiment}")
        
        # 4. 显示关键词
        if 'keyword_analysis' in analysis_result and 'top_keywords' in analysis_result['keyword_analysis']:
            print("\n4. 高频关键词 (前5个):")
            for i, keyword in enumerate(analysis_result['keyword_analysis']['top_keywords'][:5]):
                print(f"   {i+1}. {keyword['word']} ({keyword['count']}次)")
        
        # 5. 显示活跃用户
        if 'user_activity' in analysis_result and 'most_active_users' in analysis_result['user_activity']:
            print("\n5. 最活跃用户 (前3个):")
            for i, user in enumerate(analysis_result['user_activity']['most_active_users'][:3]):
                print(f"   {i+1}. {user['username']} ({user['comment_count']}条评论)")
        
        # 6. 测试从Redis获取分析结果
        print("\n6. 测试从Redis获取分析结果...")
        cached_result = get_bv_analysis(test_bv)
        if cached_result:
            print("成功从Redis获取缓存的分析结果")
        else:
            print("未找到缓存的分析结果")
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_comment_analysis() 