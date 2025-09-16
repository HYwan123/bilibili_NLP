from pymilvus import connections, Collection

class MilvusClient:
    def __init__(self, collection_name="video_recommend"):
        self.alias = "default"
        self.collection_name = collection_name
        connections.connect(self.alias, host="127.0.0.1", port="19530")
        self.collection = Collection(self.collection_name, using=self.alias)
        print(f"已连接集合: {self.collection_name}")

    def insert_vector(self, ids: list[str], embeddings: list[list[float]]) -> None:
        self.collection.insert([ids, embeddings])
        self.collection.flush()
        self.collection.load()

    def search_similar(self, query_embedding: list[float], top_k=5) -> list[str]:
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param={"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit=top_k,
            output_fields=["id"],
        )
        bvs = []
        for hits in results: # type: ignore
            for hit in hits:
                bvs.append(hit.id)
        return bvs

    def __del__(self):
        connections.disconnect(self.alias)
        print("关闭 Milvus 连接")


