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
        print("Worker: 正在加载 BERT 情感分析模型...")
        _classifier = pipeline(
            "sentiment-analysis", # type: ignore
            model="nlptown/bert-base-multilingual-uncased-sentiment"
        ) # type: ignore
    return _classifier

class CommentAnalyzer:
    def __init__(self):
        self.redis_client = RedisClientAsync()

    async def analyze_comments(self, comments: List[Dict[str, Any]], bv_id: str) -> Dict[str, Any]:
        analysis_result = {"bv_id": bv_id, "timestamp": datetime.now().isoformat()}
        try:
            if not comments: return {"error": "没有获取到视频评论数据"}
            
            # 1. 预处理
            cleaned_comments, clean_stats = self._preprocess_comments(comments)
            if not cleaned_comments:
                return {"error": "清洗后无有效语义内容", "cleaning_report": clean_stats}

            # 2. 基础统计（增强版）
            analysis_result["cleaning_report"] = clean_stats
            analysis_result["basic_stats"] = self._basic_statistics(cleaned_comments) # type: ignore
            
            # 3. 情感分析
            analysis_result["sentiment_analysis"] = await self._sentiment_analysis_pipeline(cleaned_comments) # type: ignore
            
            # 4. 关键词分析
            analysis_result["keyword_analysis"] = self._keyword_analysis(cleaned_comments) # type: ignore
            
            # 5. 用户活跃度
            analysis_result["user_activity"] = self._user_activity_analysis(cleaned_comments) # type: ignore
            
            await self.redis_client.set(f"comment_analysis_{bv_id}", json.dumps(analysis_result, ensure_ascii=False))
            await self.redis_client.add_streams(RESULT_STREAM, {'BV': bv_id})
            return analysis_result
            
        except Exception as e:
            await self.redis_client.redis_client.delete(f"comment_analysis_{bv_id}")
            error_res = {"error": f"分析引擎内部异常: {str(e)}", "bv_id": bv_id}
            await self.redis_client.set(f"comment_analysis_{bv_id}", json.dumps(error_res, ensure_ascii=False))
            await self.redis_client.add_streams(RESULT_STREAM, {'BV': bv_id})
            return error_res

    def _preprocess_comments(self, comments: List[Dict[str, Any]]) -> tuple:
        raw_count = len(comments)
        noise_details = {"check_in": 0, "spam": 0, "short_noise": 0, "lottery": 0}
        check_in_patterns = [r"打卡", r"第一", r"前排", r"来了", r"报道"]
        lottery_patterns = [r"抽奖", r"欧皇", r"转发", r"选我", r"万一呢"]
        cleaned, seen = [], set()
        for comment in comments:
            text = str(comment.get('comment_text', '')).strip()
            if text in seen or len(text) < 2:
                if text in seen: noise_details["spam"] += 1
                else: noise_details["short_noise"] += 1
                continue
            if any(re.search(p, text) for p in check_in_patterns):
                noise_details["check_in"] += 1
                continue
            if any(re.search(p, text) for p in lottery_patterns):
                noise_details["lottery"] += 1
                continue
            text = re.sub(r"\[.*?\]", "", text) 
            text = re.sub(r"http\S+", "", text)
            if len(text.strip()) >= 2:
                comment['comment_text'] = text.strip()
                cleaned.append(comment)
                seen.add(text)
        stats = {"raw_total": raw_count, "cleaned_total": len(cleaned), "filtered_out": raw_count - len(cleaned),
                 "efficiency": round((len(cleaned)/raw_count)*100, 1) if raw_count > 0 else 0,
                 "noise_breakdown": noise_details}
        return cleaned, stats

    async def _sentiment_analysis_pipeline(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        sample_size = 50
        analysis_samples = comments[:sample_size]
        texts = [str(c['comment_text'])[:200] for c in analysis_samples]
        classifier = get_classifier()
        results = await asyncio.to_thread(classifier, texts, truncation=True, padding=True, max_length=512)
        res_dict = {'negative': 0, 'neutral': 0, 'positive': 0, 'examples': []}
        for comment_obj, res in zip(analysis_samples, results):
            star = int(res["label"].split()[0])
            cat = 'negative' if star <= 2 else ('neutral' if star == 3 else 'positive')
            res_dict[cat] += 1
            res_dict['examples'].append({"comment": comment_obj['comment_text'], "label": star, "score": res["score"]})
        return res_dict

    def _basic_statistics(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        lengths = [len(str(c.get('comment_text', ''))) for c in comments]
        # 计算长度分布用于图表
        dist = {"0-20": 0, "21-50": 0, "51-100": 0, "100+": 0}
        for l in lengths:
            if l <= 20: dist["0-20"] += 1
            elif l <= 50: dist["21-50"] += 1
            elif l <= 100: dist["51-100"] += 1
            else: dist["100+"] += 1
        return {
            "total_comments": len(comments), 
            "unique_users": len(set(c.get('user_name', '') for c in comments)),
            "average_length": round(sum(lengths)/len(lengths), 1) if lengths else 0,
            "length_distribution": dist
        }

    def _keyword_analysis(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        all_text = " ".join([str(c.get('comment_text', '')) for c in comments])
        words = jieba.cut(all_text)
        stop = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '上', '也', '很', '到', '说', '要', '去', '你', '会', '吧', '那', '才'}
        filtered = [w for w in words if len(w) > 1 and w not in stop and not w.isdigit()]
        top_k = Counter(filtered).most_common(20)
        return {"top_keywords": [{"word": k, "count": v} for k, v in top_k]}

    def _user_activity_analysis(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        counts = Counter(c.get('user_name', '') for c in comments)
        most_active = counts.most_common(10)
        return {
            "most_active_users": [{"username": u, "comment_count": c} for u, c in most_active],
            "total_unique_users": len(counts)
        }

async def analyze_bv_comments(bv_id: str, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
    return await CommentAnalyzer().analyze_comments(comments, bv_id)
