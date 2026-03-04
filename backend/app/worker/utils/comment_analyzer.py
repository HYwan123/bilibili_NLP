import asyncio
import json
from typing import List, Dict, Any
from collections import Counter
import re
from datetime import datetime
import jieba
from transformers import pipeline
from app.database.redis_client_async import RedisClientAsync

RESULT_STREAM = "streams_result_isok"

# 延迟初始化分类器
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        print("Worker: 正在加载 BERT 情感分析模型 (首次加载较慢)...")
        _classifier = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment"
        )
    return _classifier

class CommentAnalyzer:
    def __init__(self):
        self.redis_client = RedisClientAsync()

    async def analyze_comments(self, comments: List[Dict[str, Any]], bv_id: str) -> Dict[str, Any]:
        """
        综合分析评论数据
        """
        analysis_result = {"bv_id": bv_id, "timestamp": datetime.now().isoformat()}
        
        try:
            if not comments:
                error_res = {"error": "没有获取到视频评论数据", **analysis_result}
                await self.redis_client.set(f"comment_analysis_{bv_id}", json.dumps(error_res, ensure_ascii=False))
                await self.redis_client.add_streams(RESULT_STREAM, {'BV': bv_id})
                return error_res
            
            print(f"Worker: 正在预处理视频 {bv_id} 的 {len(comments)} 条评论...")
            # --- 预处理环节 ---
            cleaned_comments, clean_stats = self._preprocess_comments(comments)
            
            if not cleaned_comments:
                error_res = {
                    "error": "清洗后无有效语义内容（可能全是打卡/广告/抽奖）", 
                    "cleaning_report": clean_stats, 
                    **analysis_result
                }
                await self.redis_client.set(f"comment_analysis_{bv_id}", json.dumps(error_res, ensure_ascii=False))
                await self.redis_client.add_streams(RESULT_STREAM, {'BV': bv_id})
                return error_res

            print(f"Worker: 预处理完成，剩余有效语料: {len(cleaned_comments)}")

            # 构建结果
            analysis_result["cleaning_report"] = clean_stats
            analysis_result["basic_stats"] = self._basic_statistics(cleaned_comments)
            
            # 情感分析（限制样本量以防超时）
            print(f"Worker: 正在执行情感建模分析...")
            analysis_result["sentiment_analysis"] = await self._sentiment_analysis_pipeline(cleaned_comments)
            
            # 其他分析
            analysis_result["keyword_analysis"] = self._keyword_analysis(cleaned_comments)
            analysis_result["user_activity"] = self._user_activity_analysis(cleaned_comments)
            
            # 保存最终成功结果
            await self.redis_client.set(f"comment_analysis_{bv_id}", json.dumps(analysis_result, ensure_ascii=False))
            await self.redis_client.add_streams(RESULT_STREAM, {'BV': bv_id})
            print(f"Worker: 视频 {bv_id} 分析任务圆满完成")
            return analysis_result
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_res = {"error": f"分析引擎内部异常: {str(e)}", **analysis_result}
            await self.redis_client.set(f"comment_analysis_{bv_id}", json.dumps(error_res, ensure_ascii=False))
            await self.redis_client.add_streams(RESULT_STREAM, {'BV': bv_id})
            return error_res

    def _preprocess_comments(self, comments: List[Dict[str, Any]]) -> tuple:
        """
        语料清洗：剔除噪音
        """
        raw_count = len(comments)
        noise_details = {"check_in": 0, "spam": 0, "short_noise": 0, "lottery": 0}
        
        check_in_patterns = [r"打卡", r"第一", r"前排", r"来了", r"报道"]
        lottery_patterns = [r"抽奖", r"欧皇", r"转发", r"选我", r"万一呢"]
        
        cleaned = []
        seen = set()

        for comment in comments:
            text = str(comment.get('comment_text', '')).strip()
            
            if text in seen:
                noise_details["spam"] += 1
                continue
            if len(text) < 2:
                noise_details["short_noise"] += 1
                continue
                
            if any(re.search(p, text) for p in check_in_patterns):
                noise_details["check_in"] += 1
                continue
            if any(re.search(p, text) for p in lottery_patterns):
                noise_details["lottery"] += 1
                continue

            # 正则清理
            text = re.sub(r"\[.*?\]", "", text) 
            text = re.sub(r"http\S+", "", text)
            
            if len(text.strip()) >= 2:
                comment['comment_text'] = text.strip()
                cleaned.append(comment)
                seen.add(text)

        stats = {
            "raw_total": raw_count,
            "cleaned_total": len(cleaned),
            "filtered_out": raw_count - len(cleaned),
            "efficiency": f"{round((len(cleaned)/raw_count)*100, 1)}%" if raw_count > 0 else "0%",
            "noise_breakdown": noise_details
        }
        return cleaned, stats

    async def _sentiment_analysis_pipeline(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        BERT 情感分析（限制核心样本量以保证响应速度）
        """
        # 限制只分析前 50 条最具代表性的评论（防止大型视频导致 OOM 或超时）
        sample_size = 50
        analysis_samples = comments[:sample_size]
        
        texts = [c['comment_text'] for c in analysis_samples]
        classifier = get_classifier()
        
        # 在线程池中执行耗时的 BERT 模型
        results = await asyncio.to_thread(classifier, texts)
        
        result_dict = {'negative': 0, 'neutral': 0, 'positive': 0, 'examples': []}
        
        for comment_obj, res in zip(analysis_samples, results):
            label = res["label"]
            score = res["score"]
            text = comment_obj['comment_text']
            
            # 映射模型标签到语义分类
            # 1-2 stars -> negative, 3 -> neutral, 4-5 -> positive
            star_count = int(label.split()[0])
            if star_count <= 2:
                category = 'negative'
            elif star_count == 3:
                category = 'neutral'
            else:
                category = 'positive'
                
            result_dict[category] += 1
            result_dict['examples'].append({
                "comment": text,
                "label": star_count,
                "score": score
            })

        return result_dict

    def _basic_statistics(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        comment_lengths = [len(str(c.get('comment_text', ''))) for c in comments]
        return {
            "total_comments": len(comments),
            "unique_users": len(set(c.get('user_name', '') for c in comments)),
            "average_length": round(sum(comment_lengths)/len(comment_lengths), 1) if comment_lengths else 0
        }

    def _keyword_analysis(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        all_text = " ".join([str(c.get('comment_text', '')) for c in comments])
        words = jieba.cut(all_text)
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '上', '也', '很', '到', '说', '要', '去', '你', '会'}
        filtered = [w for w in words if len(w) > 1 and w not in stop_words and not w.isdigit()]
        top_keywords = Counter(filtered).most_common(20)
        return {"top_keywords": [{"word": k, "count": v} for k, v in top_keywords]}

    def _user_activity_analysis(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        user_counts = Counter(c.get('user_name', '') for c in comments)
        most_active = user_counts.most_common(5)
        return {
            "most_active_users": [{"username": u, "comment_count": c} for u, c in most_active],
            "total_unique_users": len(user_counts)
        }

async def analyze_bv_comments(bv_id: str, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
    return await CommentAnalyzer().analyze_comments(comments, bv_id)
