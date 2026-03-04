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
                return {"error": "没有获取到视频评论数据"}
            
            print(f"Worker: 正在分析视频 {bv_id}...")
            
            # --- 预处理环节 ---
            cleaned_comments, clean_stats = self._preprocess_comments(comments)
            
            if not cleaned_comments:
                return {"error": "清洗后无有效语义内容", "cleaning_report": clean_stats}

            # 构建结果
            analysis_result["cleaning_report"] = clean_stats
            analysis_result["basic_stats"] = self._basic_statistics(cleaned_comments)
            
            # 情感分析（物理截断加固）
            analysis_result["sentiment_analysis"] = await self._sentiment_analysis_pipeline(cleaned_comments)
            
            # 其他分析
            analysis_result["keyword_analysis"] = self._keyword_analysis(cleaned_comments)
            analysis_result["user_activity"] = self._user_activity_analysis(cleaned_comments)
            
            # 【重要】仅在成功时保存到Redis，并发送完成信号
            await self.redis_client.set(f"comment_analysis_{bv_id}", json.dumps(analysis_result, ensure_ascii=False))
            await self.redis_client.add_streams(RESULT_STREAM, {'BV': bv_id})
            print(f"Worker: 视频 {bv_id} 分析成功")
            return analysis_result
            
        except Exception as e:
            print(f"Worker: 视频 {bv_id} 分析发生异常: {str(e)}")
            # 发生异常时，确保清理掉可能存在的旧错误缓存，防止前端死循环读取
            await self.redis_client.redis_client.delete(f"comment_analysis_{bv_id}")
            # 依然发送完成信号，但内容包含错误，告知前端停止等待
            error_res = {"error": f"分析引擎内部异常: {str(e)}", "bv_id": bv_id}
            await self.redis_client.set(f"comment_analysis_{bv_id}", json.dumps(error_res, ensure_ascii=False))
            await self.redis_client.add_streams(RESULT_STREAM, {'BV': bv_id})
            return error_res

    def _preprocess_comments(self, comments: List[Dict[str, Any]]) -> tuple:
        raw_count = len(comments)
        noise_details = {"check_in": 0, "spam": 0, "short_noise": 0, "lottery": 0}
        check_in_patterns = [r"打卡", r"第一", r"前排", r"来了", r"报道"]
        lottery_patterns = [r"抽奖", r"欧皇", r"转发", r"选我", r"万一呢"]
        
        cleaned = []
        seen = set()
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
                 "efficiency": f"{round((len(cleaned)/raw_count)*100, 1)}%" if raw_count > 0 else "0%",
                 "noise_breakdown": noise_details}
        return cleaned, stats

    async def _sentiment_analysis_pipeline(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        # 激进截断：中文环境下 200 字符通常对应 300~400 tokens，远低于 512 的上限
        sample_size = 50
        analysis_samples = comments[:sample_size]
        texts = [str(c['comment_text'])[:200] for c in analysis_samples]
        
        classifier = get_classifier()
        # 增加显式 truncation 和 padding 参数
        results = await asyncio.to_thread(classifier, texts, truncation=True, padding=True, max_length=512)
        
        result_dict = {'negative': 0, 'neutral': 0, 'positive': 0, 'examples': []}
        for comment_obj, res in zip(analysis_samples, results):
            star_count = int(res["label"].split()[0])
            category = 'negative' if star_count <= 2 else ('neutral' if star_count == 3 else 'positive')
            result_dict[category] += 1
            result_dict['examples'].append({"comment": comment_obj['comment_text'], "label": star_count, "score": res["score"]})
        return result_dict

    def _basic_statistics(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        lengths = [len(str(c.get('comment_text', ''))) for c in comments]
        return {"total_comments": len(comments), "unique_users": len(set(c.get('user_name', '') for c in comments)),
                "average_length": round(sum(lengths)/len(lengths), 1) if lengths else 0}

    def _keyword_analysis(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        all_text = " ".join([str(c.get('comment_text', '')) for c in comments])
        words = jieba.cut(all_text)
        stop = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '上', '也', '很', '到', '说', '要', '去', '你', '会'}
        filtered = [w for w in words if len(w) > 1 and w not in stop and not w.isdigit()]
        return {"top_keywords": [{"word": k, "count": v} for k, v in Counter(filtered).most_common(20)]}

    def _user_activity_analysis(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        counts = Counter(c.get('user_name', '') for c in comments)
        return {"most_active_users": [{"username": u, "comment_count": c} for u, c in counts.most_common(5)],
                "total_unique_users": len(counts)}

async def analyze_bv_comments(bv_id: str, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
    return await CommentAnalyzer().analyze_comments(comments, bv_id)
