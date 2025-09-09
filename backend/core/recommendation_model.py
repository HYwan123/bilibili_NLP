import json
import requests
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter, defaultdict
import redis
import numpy as np
from datetime import datetime, timedelta
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import core.sql_use as sql_use

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class ContentRecommendationModel:
    def __init__(self):
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.headers = {
            "Authorization": "Bearer sk-skgydfquljaaecqxaqyumvbhnurbzqovgynlvcadxwpfifux",
            "Content-Type": "application/json"
        }
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words=None)
        
    def analyze_user_preferences(self, user_comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析用户偏好
        """
        if not user_comments:
            return {"error": "没有用户评论数据"}
        
        # 提取用户评论文本
        comment_texts = [comment.get('comment_text', '') for comment in user_comments]
        all_text = ' '.join(comment_texts)
        
        # 关键词提取
        words = jieba.cut(all_text)
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        filtered_words = [word for word in words if len(word) > 1 and word not in stop_words and not word.isdigit()]
        
        # 统计词频
        word_freq = Counter(filtered_words)
        top_keywords = word_freq.most_common(20)
        
        # 分析评论情感倾向
        positive_words = ['好', '棒', '赞', '喜欢', '爱', '优秀', '精彩', '厉害', '不错', '支持']
        negative_words = ['差', '烂', '垃圾', '讨厌', '恶心', '无聊', '失望', '糟糕']
        
        positive_count = sum(1 for text in comment_texts for word in positive_words if word in text)
        negative_count = sum(1 for text in comment_texts for word in negative_words if word in text)
        
        # 分析活跃时间（如果有时间戳）
        activity_pattern = self._analyze_activity_pattern(user_comments)
        
        # 分析评论长度偏好
        comment_lengths = [len(text) for text in comment_texts]
        avg_length = np.mean(comment_lengths) if comment_lengths else 0
        
        # 分析内容类型偏好
        content_preferences = self._analyze_content_preferences(comment_texts)
        
        preferences = {
            "user_keywords": [{"word": word, "count": count} for word, count in top_keywords],
            "sentiment_tendency": {
                "positive": positive_count,
                "negative": negative_count,
                "ratio": positive_count / (positive_count + negative_count + 1)
            },
            "activity_pattern": activity_pattern,
            "comment_style": {
                "average_length": round(avg_length, 2),
                "total_comments": len(comment_texts),
                "engagement_level": self._calculate_engagement_level(comment_texts)
            },
            "content_preferences": content_preferences
        }
        
        return preferences
    
    def _analyze_activity_pattern(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析用户活跃模式
        """
        # 这里可以根据评论的时间戳分析用户的活跃时间
        # 由于示例数据可能没有时间戳，我们提供一个基础实现
        return {
            "most_active_hours": [20, 21, 22],  # 假设晚上8-10点最活跃
            "activity_frequency": "medium",
            "consistency": 0.7
        }
    
    def _analyze_content_preferences(self, comment_texts: List[str]) -> Dict[str, Any]:
        """
        分析内容偏好
        """
        # 定义内容类型关键词
        content_categories = {
            "游戏": ["游戏", "玩", "操作", "技能", "装备", "角色", "副本", "PK", "升级"],
            "音乐": ["音乐", "歌", "唱", "声音", "旋律", "节奏", "歌手", "专辑"],
            "科技": ["科技", "技术", "AI", "编程", "代码", "算法", "数据", "软件"],
            "生活": ["生活", "日常", "分享", "经验", "美食", "旅行", "购物"],
            "娱乐": ["搞笑", "有趣", "娱乐", "综艺", "明星", "八卦", "电影", "电视剧"],
            "教育": ["学习", "教程", "知识", "教育", "课程", "讲解", "分析", "研究"]
        }
        
        category_scores = {}
        all_text = ' '.join(comment_texts)
        
        for category, keywords in content_categories.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            category_scores[category] = score
        
        # 排序并返回前3个偏好
        sorted_preferences = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "top_categories": sorted_preferences[:3],
            "category_distribution": category_scores
        }
    
    def _calculate_engagement_level(self, comment_texts: List[str]) -> str:
        """
        计算用户参与度
        """
        if not comment_texts:
            return "low"
        
        avg_length = np.mean([len(text) for text in comment_texts])
        
        if avg_length > 50:
            return "high"
        elif avg_length > 20:
            return "medium"
        else:
            return "low"
    
    def generate_recommendations(self, user_preferences: Dict[str, Any], available_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        基于用户偏好生成推荐
        """
        if not user_preferences or not available_content:
            return []
        
        recommendations = []
        user_keywords = [item['word'] for item in user_preferences.get('user_keywords', [])]
        user_categories = [cat[0] for cat in user_preferences.get('content_preferences', {}).get('top_categories', [])]
        
        for content in available_content:
            score = self._calculate_recommendation_score(content, user_keywords, user_categories, user_preferences)
            if score > 0.3:  # 阈值过滤
                recommendations.append({
                    **content,
                    "recommendation_score": round(score, 3),
                    "reason": self._generate_recommendation_reason(content, user_preferences)
                })
        
        # 按推荐分数排序
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        return recommendations[:10]  # 返回前10个推荐
    
    def _calculate_recommendation_score(self, content: Dict[str, Any], user_keywords: List[str], 
                                     user_categories: List[str], user_preferences: Dict[str, Any]) -> float:
        """
        计算推荐分数
        """
        score = 0.0
        
        # 关键词匹配分数 (40%)
        content_text = content.get('title', '') + ' ' + content.get('description', '')
        keyword_matches = sum(1 for keyword in user_keywords if keyword in content_text)
        keyword_score = min(keyword_matches / len(user_keywords) if user_keywords else 0, 1.0) * 0.4
        
        # 类别匹配分数 (30%)
        content_category = content.get('category', '')
        category_score = 0.3 if content_category in user_categories else 0
        
        # 热度分数 (20%)
        view_count = content.get('view_count', 0)
        popularity_score = min(view_count / 1000000, 1.0) * 0.2  # 标准化到百万播放量
        
        # 时效性分数 (10%)
        pub_date = content.get('pub_date')
        recency_score = self._calculate_recency_score(pub_date) * 0.1
        
        score = keyword_score + category_score + popularity_score + recency_score
        return min(score, 1.0)
    
    def _calculate_recency_score(self, pub_date: Optional[str]) -> float:
        """
        计算时效性分数
        """
        if not pub_date:
            return 0.5
        
        try:
            pub_datetime = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
            days_ago = (datetime.now() - pub_datetime).days
            
            if days_ago <= 7:
                return 1.0
            elif days_ago <= 30:
                return 0.8
            elif days_ago <= 90:
                return 0.6
            else:
                return 0.3
        except:
            return 0.5
    
    def _generate_recommendation_reason(self, content: Dict[str, Any], user_preferences: Dict[str, Any]) -> str:
        """
        生成推荐理由
        """
        reasons = []
        
        # 检查关键词匹配
        user_keywords = [item['word'] for item in user_preferences.get('user_keywords', [])[:5]]
        content_text = content.get('title', '') + ' ' + content.get('description', '')
        matched_keywords = [kw for kw in user_keywords if kw in content_text]
        
        if matched_keywords:
            reasons.append(f"包含您感兴趣的关键词: {', '.join(matched_keywords[:3])}")
        
        # 检查类别匹配
        user_categories = [cat[0] for cat in user_preferences.get('content_preferences', {}).get('top_categories', [])]
        content_category = content.get('category', '')
        if content_category in user_categories:
            reasons.append(f"属于您偏好的{content_category}类别")
        
        # 检查热度
        view_count = content.get('view_count', 0)
        if view_count > 100000:
            reasons.append("热门内容，播放量较高")
        
        return "; ".join(reasons) if reasons else "基于您的浏览历史推荐"
    
    def get_similar_users(self, target_user_id: int, all_users_data: Dict[int, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        找到相似用户
        """
        if target_user_id not in all_users_data:
            return []
        
        target_preferences = self.analyze_user_preferences(all_users_data[target_user_id])
        target_keywords = set(item['word'] for item in target_preferences.get('user_keywords', []))
        
        similar_users = []
        
        for user_id, comments in all_users_data.items():
            if user_id == target_user_id:
                continue
            
            user_preferences = self.analyze_user_preferences(comments)
            user_keywords = set(item['word'] for item in user_preferences.get('user_keywords', []))
            
            # 计算关键词相似度
            if target_keywords and user_keywords:
                similarity = len(target_keywords & user_keywords) / len(target_keywords | user_keywords)
                if similarity > 0.2:  # 相似度阈值
                    similar_users.append({
                        "user_id": user_id,
                        "similarity": round(similarity, 3),
                        "common_interests": list(target_keywords & user_keywords)
                    })
        
        similar_users.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_users[:5]  # 返回前5个相似用户
    
    def collaborative_filtering_recommendations(self, target_user_id: int, similar_users: List[Dict[str, Any]], 
                                             all_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        协同过滤推荐
        """
        recommendations = []
        
        # 获取相似用户喜欢的内容
        similar_user_preferences = {}
        for similar_user in similar_users:
            user_id = similar_user['user_id']
            # 这里可以获取相似用户的历史行为数据
            # 简化实现：基于相似度权重推荐
            weight = similar_user['similarity']
            similar_user_preferences[user_id] = weight
        
        # 基于协同过滤生成推荐
        for content in all_content:
            score = 0
            for user_id, weight in similar_user_preferences.items():
                # 这里可以加入更复杂的评分逻辑
                score += weight * 0.5  # 简化的评分
            
            if score > 0.3:
                recommendations.append({
                    **content,
                    "cf_score": round(score, 3),
                    "recommendation_type": "collaborative_filtering"
                })
        
        recommendations.sort(key=lambda x: x['cf_score'], reverse=True)
        return recommendations[:5]
    
    def save_recommendations_to_redis(self, user_id: int, recommendations: List[Dict[str, Any]]):
        """
        保存推荐结果到Redis
        """
        key = f"user_recommendations_{user_id}"
        data = {
            "timestamp": datetime.now().isoformat(),
            "recommendations": recommendations
        }
        redis_client.set(key, json.dumps(data, ensure_ascii=False), ex=3600)  # 1小时过期
    
    def get_recommendations_from_redis(self, user_id: int) -> List[Dict[str, Any]]:
        """
        从Redis获取推荐结果
        """
        key = f"user_recommendations_{user_id}"
        data = redis_client.get(key)
        if data:
            try:
                result = json.loads(str(data))
                return result.get('recommendations', [])
            except:
                return []
        return []
    
    def generate_content_based_recommendations(self, user_comments: List[Dict[str, Any]], 
                                            available_videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        基于内容的推荐算法
        """
        try:
            # 分析用户偏好
            user_preferences = self.analyze_user_preferences(user_comments)
            
            # 使用AI模型生成智能推荐
            ai_recommendations = self._generate_ai_recommendations(user_preferences, available_videos)
            
            # 结合传统算法和AI推荐
            content_recommendations = self.generate_recommendations(user_preferences, available_videos)
            
            # 合并和去重
            all_recommendations = []
            seen_ids = set()
            
            # 优先AI推荐
            for rec in ai_recommendations:
                if rec.get('video_id') not in seen_ids:
                    all_recommendations.append(rec)
                    seen_ids.add(rec.get('video_id'))
            
            # 补充传统推荐
            for rec in content_recommendations:
                if rec.get('video_id') not in seen_ids and len(all_recommendations) < 10:
                    all_recommendations.append(rec)
                    seen_ids.add(rec.get('video_id'))
            
            return all_recommendations
            
        except Exception as e:
            print(f"推荐生成失败: {e}")
            return []
    
    def _generate_ai_recommendations(self, user_preferences: Dict[str, Any], 
                                   available_videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        使用AI模型生成推荐
        """
        try:
            # 构建用户画像描述
            user_profile = self._build_user_profile_text(user_preferences)
            
            # 构建可选视频列表
            video_list = []
            for i, video in enumerate(available_videos[:20]):  # 限制数量避免token过多
                video_info = f"{i+1}. 标题: {video.get('title', '')}, 分类: {video.get('category', '')}, 描述: {video.get('description', '')[:100]}"
                video_list.append(video_info)
            
            videos_text = "\n".join(video_list)
            
            prompt = f"""基于用户画像，从以下视频列表中推荐最适合的5个视频。

用户画像：
{user_profile}

可选视频列表：
{videos_text}

请分析用户的兴趣偏好，选择最匹配的视频，并用JSON格式返回结果：
{{
    "recommendations": [
        {{
            "video_index": 1,
            "match_score": 0.85,
            "reason": "推荐理由"
        }}
    ]
}}"""

            data = {
                "model": "Qwen/QwQ-32B",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "max_tokens": 1000,
                "temperature": 0.3
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                try:
                    ai_result = json.loads(content)
                    recommendations = []
                    
                    for rec in ai_result.get('recommendations', []):
                        video_index = rec.get('video_index', 1) - 1
                        if 0 <= video_index < len(available_videos):
                            video = available_videos[video_index].copy()
                            video['ai_score'] = rec.get('match_score', 0.5)
                            video['ai_reason'] = rec.get('reason', '')
                            video['recommendation_type'] = 'ai_based'
                            recommendations.append(video)
                    
                    return recommendations
                    
                except json.JSONDecodeError:
                    return []
            
            return []
            
        except Exception as e:
            print(f"AI推荐失败: {e}")
            return []
    
    def _build_user_profile_text(self, user_preferences: Dict[str, Any]) -> str:
        """
        构建用户画像文本描述
        """
        profile_parts = []
        
        # 关键词偏好
        keywords = user_preferences.get('user_keywords', [])[:10]
        if keywords:
            keyword_text = ", ".join([item['word'] for item in keywords])
            profile_parts.append(f"关键词偏好: {keyword_text}")
        
        # 内容类别偏好
        categories = user_preferences.get('content_preferences', {}).get('top_categories', [])
        if categories:
            category_text = ", ".join([cat[0] for cat in categories[:3]])
            profile_parts.append(f"内容类别偏好: {category_text}")
        
        # 情感倾向
        sentiment = user_preferences.get('sentiment_tendency', {})
        ratio = sentiment.get('ratio', 0.5)
        if ratio > 0.7:
            profile_parts.append("情感倾向: 积极正面")
        elif ratio < 0.3:
            profile_parts.append("情感倾向: 较为挑剔")
        else:
            profile_parts.append("情感倾向: 中性客观")
        
        # 参与度
        engagement = user_preferences.get('comment_style', {}).get('engagement_level', 'medium')
        profile_parts.append(f"参与度: {engagement}")
        
        return "; ".join(profile_parts)


def recommend_for_user(user_id: int, user_comments: List[Dict[str, Any]], 
                      available_content: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    为用户生成推荐的便捷函数
    """
    model = ContentRecommendationModel()
    
    # 如果没有提供可用内容，使用默认示例数据
    if not available_content:
        available_content = get_sample_video_data()
    
    # 生成推荐
    recommendations = model.generate_content_based_recommendations(user_comments, available_content)
    
    # 分析用户偏好
    user_preferences = model.analyze_user_preferences(user_comments)
    
    result = {
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "user_preferences": user_preferences,
        "recommendations": recommendations,
        "total_recommendations": len(recommendations)
    }
    
    # 保存到Redis
    model.save_recommendations_to_redis(user_id, recommendations)
    
    return result


def get_sample_video_data() -> List[Dict[str, Any]]:
    """
    爬取B站热门视频数据
    """
    import time
    import random
    
    def fetch_bilibili_videos(search_keywords: Optional[List[str]] = None, max_videos: int = 20) -> List[Dict[str, Any]]:
        """
        爬取B站视频数据
        """
        videos = []
        
        # 如果没有提供搜索关键词，使用默认的热门关键词
        if not search_keywords:
            search_keywords = ["编程", "游戏", "美食", "音乐", "科技", "生活", "娱乐", "学习"]
        r = sql_use.SQL_redis().get_client()
        cookie = r.get('video_select_cookie') # type: ignore
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cookie': cookie
        }
        
        try:
            for keyword in search_keywords[:4]:  # 限制关键词数量
                try:
                    # B站搜索API
                    search_url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={keyword}&page=1&page_size=20"

                    
                    response = requests.get(search_url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(data)
                        if data.get('code') == 0 and 'data' in data:
                            result_data = data['data']
                            video_list = result_data.get('result', [])
                            
                            for video in video_list:
                                try:
                                    # 提取视频信息
                                    video_info = {
                                        "video_id": video.get('bvid', ''),
                                        "title": video.get('title', '').replace('<em class="keyword">', '').replace('</em>', ''),
                                        "category": _get_category_by_keyword(keyword),
                                        "description": video.get('description', '')[:200],  # 限制描述长度
                                        "view_count": video.get('play', 0),
                                        "pub_date": _format_timestamp(video.get('pubdate', 0)),
                                        "author": video.get('author', ''),
                                        "duration": _format_duration(video.get('duration', '')),
                                        "pic": video.get('pic', ''),
                                        "tag": video.get('tag', ''),
                                        "keyword": keyword
                                    }
                                    
                                    if video_info['video_id'] and video_info['title']:
                                        videos.append(video_info)
                                        
                                except Exception as e:
                                    print(f"解析视频数据失败: {e}")
                                    continue
                    
                    # 添加延时避免请求过快
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    print(f"搜索关键词 '{keyword}' 失败: {e}")
                    continue
            
            # 如果爬取失败，返回备用数据
            if not videos:
                print("爬取失败，使用备用数据")
                return _get_fallback_data()
            
            # 去重并限制数量
            unique_videos = []
            seen_ids = set()
            for video in videos:
                if video['video_id'] not in seen_ids:
                    unique_videos.append(video)
                    seen_ids.add(video['video_id'])
                    if len(unique_videos) >= max_videos:
                        break
            
            return unique_videos
            
        except Exception as e:
            print(f"爬取视频数据失败: {e}")
            return _get_fallback_data()
    
    def _get_category_by_keyword(keyword: str) -> str:
        """
        根据关键词映射分类
        """
        category_map = {
            "编程": "科技",
            "游戏": "游戏", 
            "美食": "生活",
            "音乐": "音乐",
            "科技": "科技",
            "生活": "生活",
            "娱乐": "娱乐",
            "学习": "教育"
        }
        return category_map.get(keyword, "其他")
    
    def _format_timestamp(timestamp: int) -> str:
        """
        格式化时间戳
        """
        try:
            if timestamp:
                dt = datetime.fromtimestamp(timestamp)
                return dt.isoformat() + 'Z'
            return datetime.now().isoformat() + 'Z'
        except:
            return datetime.now().isoformat() + 'Z'
    
    def _format_duration(duration_str: str) -> str:
        """
        格式化视频时长
        """
        try:
            if isinstance(duration_str, str) and ':' in duration_str:
                return duration_str
            elif isinstance(duration_str, int):
                minutes = duration_str // 60
                seconds = duration_str % 60
                return f"{minutes:02d}:{seconds:02d}"
            return "00:00"
        except:
            return "00:00"
    
    def _get_fallback_data() -> List[Dict[str, Any]]:
        """
        备用数据，当爬取失败时使用
        """
        return [
            {
                "video_id": "BV114514",
                "title": "爬取失败",
                "category": "科技",
                "description": "爬取失败",
                "view_count": 150000,
                "pub_date": "2024-01-15T10:00:00Z",
                "author": "爬取失败",
                "duration": "45:30",
                "pic": "",
                "tag": "编程,Python,教程",
                "keyword": "编程"
            }
           
        ]
    
    # 执行爬取
    try:
        print("开始爬取B站视频数据...")
        videos = fetch_bilibili_videos()
        print(f"成功爬取 {len(videos)} 个视频")
        return videos
    except Exception as e:
        print(f"爬取过程出错: {e}")
        return _get_fallback_data()
