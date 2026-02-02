from pymilvus import AsyncMilvusClient

class MilvusClient:
    _instance = None
    _initialized = False
    def __new__(cls):

        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    

    def __init__(self, collection_name="video_recommend"):
        if MilvusClient._initialized:
            return
        self.alias = "default"
        self.collection_name = collection_name
        self.collection = AsyncMilvusClient(uri="http://127.0.0.1:19530")

        print(f"已连接集合: {self.collection_name}")
        MilvusClient._initialized = True

    async def insert_vector(self, video_ids: list[str], embeddings: list[list[float]]) -> None:
        # 只插入video_id和embedding，id字段会自动生成
        entities = []
        for vid, emb in zip(video_ids, embeddings):
            entities.append({
                "video_id": vid,   # 确保这里传入的是 string 类型 (VARCHAR)
                "embedding": emb   # 确保这里传入的是 float list 类型 (FLOAT_VECTOR)
            })

        await self.collection.insert(collection_name=self.collection_name, data=entities)


    async def search_similar(self, query_embedding: list[float], top_k=5) -> list[str]:
        results = await self.collection.search(
                collection_name=self.collection_name,
                data=[query_embedding],
                anns_field="embedding",
                limit=top_k,
                output_fields=["video_id"],
                metric_type="COSINE", 
                params={"nprobe": 10},
            )
        video_ids = []
        for hits in results: # type: ignore
            for hit in hits: 
                video_ids.append(hit.video_id)# type: ignore
        return video_ids

