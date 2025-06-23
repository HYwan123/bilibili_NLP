import json
import requests
from typing import List, Dict, Any, Tuple
from collections import Counter
import re
from datetime import datetime
import jieba
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class CommentAnalyzer:
    def __init__(self):
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.headers = {
            "Authorization": "Bearer sk-skgydfquljaaecqxaqyumvbhnurbzqovgynlvcadxwpfifux",
            "Content-Type": "application/json"
        }
    
    def analyze_comments(self, comments: List[Dict[str, Any]], bv_id: str) -> Dict[str, Any]:
        """
        综合分析评论数据
        """
        if not comments:
            return {"error": "没有评论数据"}
        
        analysis_result = {
            "bv_id": bv_id,
            "timestamp": datetime.now().isoformat(),
            "basic_stats": self._basic_statistics(comments),
            "sentiment_analysis": self._sentiment_analysis(comments),
            "keyword_analysis": self._keyword_analysis(comments),
            "user_activity": self._user_activity_analysis(comments),
            "content_quality": self._content_quality_analysis(comments)
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
    
    def _sentiment_analysis(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        情感分析
        """
        try:
            # 选择前20条评论进行情感分析，避免token过多
            sample_comments = comments[:20]
            comments_text = "\n".join([f"{i+1}. {comment.get('comment_text', '')}" 
                                     for i, comment in enumerate(sample_comments)])
            
            prompt = f"""请分析以下B站视频评论的情感倾向，请从以下几个方面进行分析：

1. 整体情感倾向：正面、负面、中性评论的比例
2. 主要情感类型：欢乐、愤怒、悲伤、惊讶、期待等
3. 情感强度：强烈、中等、轻微
4. 情感关键词：提取体现情感的关键词汇

请用JSON格式返回结果，包含以下字段：
- overall_sentiment: 整体情感倾向（positive/negative/neutral）
- sentiment_distribution: 情感分布比例
- emotion_types: 主要情感类型
- intensity: 情感强度分布
- keywords: 情感关键词列表

评论内容：
{comments_text}"""

            data = {
                "model": "Qwen/QwQ-32B",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "max_tokens": 800,
                "temperature": 0.3
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # 尝试解析JSON响应
                try:
                    sentiment_result = json.loads(content)
                    return sentiment_result
                except json.JSONDecodeError:
                    # 如果JSON解析失败，返回文本分析结果
                    return {
                        "overall_sentiment": "neutral",
                        "analysis_text": content,
                        "sample_size": len(sample_comments)
                    }
            else:
                return {"error": f"情感分析API调用失败: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"情感分析失败: {str(e)}"}
    
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
    
    def _content_quality_analysis(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        内容质量分析
        """
        try:
            # 分析评论质量指标
            quality_metrics = []
            
            for comment in comments:
                text = comment.get('comment_text', '')
                length = len(text)
                
                # 简单的质量评分算法
                quality_score = 0
                
                # 长度评分（0-30分）
                if length >= 50:
                    quality_score += 30
                elif length >= 20:
                    quality_score += 20
                elif length >= 10:
                    quality_score += 10
                
                # 内容多样性评分（0-20分）
                unique_chars = len(set(text))
                if unique_chars >= 20:
                    quality_score += 20
                elif unique_chars >= 10:
                    quality_score += 15
                elif unique_chars >= 5:
                    quality_score += 10
                
                # 标点符号使用评分（0-20分）
                punctuation_count = len(re.findall(r'[，。！？；：""''（）【】]', text))
                if punctuation_count >= 3:
                    quality_score += 20
                elif punctuation_count >= 1:
                    quality_score += 10
                
                # 表情符号使用评分（0-15分）
                emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]', text))
                if emoji_count > 0:
                    quality_score += min(emoji_count * 5, 15)
                
                # 避免重复字符扣分
                if re.search(r'(.)\1{4,}', text):  # 连续5个相同字符
                    quality_score -= 10
                
                quality_score = max(0, min(100, quality_score))  # 限制在0-100分
                quality_metrics.append(quality_score)
            
            avg_quality = sum(quality_metrics) / len(quality_metrics) if quality_metrics else 0
            
            # 质量分布
            high_quality = len([q for q in quality_metrics if q >= 70])
            medium_quality = len([q for q in quality_metrics if 40 <= q < 70])
            low_quality = len([q for q in quality_metrics if q < 40])
            
            return {
                "average_quality_score": round(avg_quality, 2),
                "quality_distribution": {
                    "high": high_quality,
                    "medium": medium_quality,
                    "low": low_quality
                },
                "quality_metrics": quality_metrics[:10]  # 只返回前10个评分作为示例
            }
            
        except Exception as e:
            return {"error": f"内容质量分析失败: {str(e)}"}
    
    def get_analysis_from_redis(self, bv_id: str) -> Dict[str, Any]:
        """
        从Redis获取评论分析结果
        """
        data = redis_client.get(f"comment_analysis_{bv_id}")
        if data:
            try:
                return json.loads(data)
            except Exception as e:
                print(f"Redis数据解析失败: {e}")
                return {}
        return {}

def analyze_bv_comments(bv_id: str, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    便捷函数：分析BV评论
    """
    analyzer = CommentAnalyzer()
    return analyzer.analyze_comments(comments, bv_id)

def get_bv_analysis(bv_id: str) -> Dict[str, Any]:
    """
    便捷函数：获取BV评论分析结果
    """
    analyzer = CommentAnalyzer()
    return analyzer.get_analysis_from_redis(bv_id) 