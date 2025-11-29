import asyncio
import json
from typing import List, Dict, Any, Tuple
from collections import Counter
import re
from datetime import datetime
import jieba
import redis
import httpx
from transformers import pipeline

# 使用多语言模型
classifier = pipeline(
    "sentiment-analysis", # type: ignore
    model="nlptown/bert-base-multilingual-uncased-sentiment"
) # type: ignore

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class CommentAnalyzer:
    def __init__(self):
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.headers = {
            "Authorization": "Bearer sk-skgydfquljaaecqxaqyumvbhnurbzqovgynlvcadxwpfifux",
            "Content-Type": "application/json"
        }
    
    async def analyze_comments(self, comments: List[Dict[str, Any]], bv_id: str) -> Dict[str, Any]:
        """
        综合分析评论数据
        """
        if not comments:
            return {"error": "没有评论数据"}
        print(comments)
        analysis_result = {
            "bv_id": bv_id,
            "timestamp": datetime.now().isoformat(),
            "basic_stats": self._basic_statistics(comments),
            "sentiment_analysis": await self._sentiment_analysis_pipeline(comments),
            "keyword_analysis": self._keyword_analysis(comments),
            "user_activity": self._user_activity_analysis(comments),
        }
        
        # 保存分析结果到Redis
        redis_client.set(f"comment_analysis_{bv_id}", json.dumps(analysis_result, ensure_ascii=False))
        
        return analysis_result
    
    def _basic_statistics(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        基础统计分析
        """
        total_comments = len(comments)
        unique_users = len(set(comment.get('user_name', '') for comment in comments))
        
        # 计算评论长度统计
        comment_lengths = [len(comment.get('comment_text', '')) for comment in comments]
        avg_length = sum(comment_lengths) / len(comment_lengths) if comment_lengths else 0
        
        # 长度分布
        short_comments = len([l for l in comment_lengths if l <= 20])
        medium_comments = len([l for l in comment_lengths if 20 < l <= 100])
        long_comments = len([l for l in comment_lengths if l > 100])
        
        return {
            "total_comments": total_comments,
            "unique_users": unique_users,
            "average_length": round(avg_length, 2),
            "length_distribution": {
                "short": short_comments,
                "medium": medium_comments,
                "long": long_comments
            },
            "max_length": max(comment_lengths) if comment_lengths else 0,
            "min_length": min(comment_lengths) if comment_lengths else 0
        }
    @staticmethod
    def _which_label(text: str) -> str:
        if text == '1 star' or text == '2 stars':
            return 'negative'
        elif text == '3 stars':
            return 'neutral'
        else: return 'positive'
 
    async def _sentiment_analysis_pipeline(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        texts = [comment['comment_text'] for comment in comments]
        # 因为 classifier 是同步的，所以用 asyncio.to_thread 在线程中执行
        results = await asyncio.to_thread(classifier, texts)
        result_dict = {}
        result_dict['negative'] = 0
        result_dict['neutral'] = 0
        result_dict['positive'] = 0
        for comment, result in zip(comments, results):
            # result 本身是字典，直接存储
            result_dict[self._which_label(result["label"])] += 1
            result_dict[comment['comment_text']] = result

        return result_dict

    def _keyword_analysis(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        关键词分析
        """
        try:
            # 合并所有评论文本
            all_text = " ".join([comment.get('comment_text', '') for comment in comments])
            
            # 使用jieba进行中文分词
            words = jieba.cut(all_text)
            
            # 过滤停用词和短词
            stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
            filtered_words = [word for word in words if len(word) > 1 and word not in stop_words and not word.isdigit()]
            
            # 统计词频
            word_freq = Counter(filtered_words)
            top_keywords = word_freq.most_common(20)
            
            # 提取短语（2-3个词的组合）
            phrases = []
            for comment in comments:
                text = comment.get('comment_text', '')
                words = list(jieba.cut(text))
                for i in range(len(words) - 1):
                    phrase = words[i] + words[i+1]
                    if len(phrase) >= 4:
                        phrases.append(phrase)
            
            phrase_freq = Counter(phrases)
            top_phrases = phrase_freq.most_common(10)
            
            return {
                "top_keywords": [{"word": word, "count": count} for word, count in top_keywords],
                "top_phrases": [{"phrase": phrase, "count": count} for phrase, count in top_phrases],
                "total_unique_words": len(set(filtered_words))
            }
            
        except Exception as e:
            return {"error": f"关键词分析失败: {str(e)}"}
    
    def _user_activity_analysis(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        用户活跃度分析
        """
        try:
            # 统计每个用户的评论数量
            user_comment_count = Counter(comment.get('user_name', '') for comment in comments)
            
            # 找出最活跃的用户
            most_active_users = user_comment_count.most_common(10)
            
            # 计算活跃度分布
            comment_counts = list(user_comment_count.values())
            single_comment_users = len([count for count in comment_counts if count == 1])
            multiple_comment_users = len([count for count in comment_counts if count > 1])
            
            # 计算平均每个用户的评论数
            avg_comments_per_user = sum(comment_counts) / len(comment_counts) if comment_counts else 0
            
            return {
                "most_active_users": [{"username": user, "comment_count": count} for user, count in most_active_users],
                "activity_distribution": {
                    "single_comment_users": single_comment_users,
                    "multiple_comment_users": multiple_comment_users
                },
                "average_comments_per_user": round(avg_comments_per_user, 2),
                "total_unique_users": len(user_comment_count)
            }
            
        except Exception as e:
            return {"error": f"用户活跃度分析失败: {str(e)}"}
    
    
    def get_analysis_from_redis(self, bv_id: str) -> Dict[str, Any]:
        """
        从Redis获取评论分析结果
        """
        data = redis_client.get(f"comment_analysis_{bv_id}")
        if data:
            try:
                return json.loads(data) # type: ignore
            except Exception as e:
                print(f"Redis数据解析失败: {e}")
                return {}
        return {}

async def analyze_bv_comments(bv_id: str, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    便捷函数：分析BV评论
    """
    analyzer = CommentAnalyzer()
    return await analyzer.analyze_comments(comments, bv_id)

def get_bv_analysis(bv_id: str) -> Dict[str, Any]:
    """
    便捷函数：获取BV评论分析结果
    """
    analyzer = CommentAnalyzer()
    return analyzer.get_analysis_from_redis(bv_id)
