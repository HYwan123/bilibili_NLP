import json
from sentence_transformers import SentenceTransformer
from core import sql_use, bilibili_video_info, millvus_use

redis = sql_use.SQL_redis()
model = SentenceTransformer("BAAI/bge-base-zh")  # 768维
millvus = millvus_use.MilvusClient()

def insert_vector_by_BV(BVid: str) -> None:
    tags = bilibili_video_info.get_video_tags(BVid)
    tags_str = " ".join(tags)
    embeddings = model.encode(tags_str).tolist()
    millvus.insert_vector([BVid], [embeddings])

def get_tuijian_bvs(user_id: str) -> list[str] | None:
    raw = redis.redis_select_by_key(user_id)  # bytes
    if not raw:
        return None
    raw_str = raw.decode("utf-8")
    comments = json.loads(raw_str)
    all_text = " ".join(comment["comment_text"] for comment in comments)
    results = millvus.search_similar(model.encode(all_text).tolist())
    return results


