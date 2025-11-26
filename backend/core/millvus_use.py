from pymilvus import connections, Collection

class MilvusClient:
    def __init__(self, collection_name="video_recommend"):
        self.alias = "default"
        self.collection_name = collection_name
        connections.connect(self.alias, host="127.0.0.1", port="19530")
        self.collection = Collection(self.collection_name, using=self.alias)
        print(f"已连接集合: {self.collection_name}")

    def insert_vector(self, video_ids: list[str], embeddings: list[list[float]]) -> None:
        # 只插入video_id和embedding，id字段会自动生成
        entities = [video_ids, embeddings]
        self.collection.insert(entities)
        self.collection.flush()
        self.collection.load()

    def search_similar(self, query_embedding: list[float], top_k=5) -> list[str]:
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param={"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit=top_k,
            output_fields=["video_id"],
        )
        video_ids = []
        for hits in results: # type: ignore
            for hit in hits:
                video_ids.append(hit.video_id)
        return video_ids

    def __del__(self):
        connections.disconnect(self.alias)
        print("关闭 Milvus 连接")
