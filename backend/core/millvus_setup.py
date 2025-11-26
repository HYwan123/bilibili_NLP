from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

def create_milvus_collection(collection_name="video_recommend"):
    """
    创建Milvus集合，定义正确的模式
    """
    try:
        # 连接到Milvus
        connections.connect("default", host="127.0.0.1", port="19530")
        
        # 定义字段
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="video_id", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)  # BGE-base模型输出768维向量
        ]
        
        # 创建集合模式
        schema = CollectionSchema(fields, description="Video recommendation collection")
        
        # 创建集合
        collection = Collection(name=collection_name, schema=schema)
        
        # 创建索引
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 1024}
        }
        
        collection.create_index(field_name="embedding", index_params=index_params)
        
        print(f"集合 {collection_name} 创建成功")
        return True
        
    except Exception as e:
        print(f"创建集合失败: {e}")
        return False
    finally:
        connections.disconnect("default")

def recreate_collection_with_correct_schema(collection_name="video_recommend"):
    """
    删除现有集合并创建具有正确模式的新集合
    """
    try:
        connections.connect("default", host="127.0.0.1", port="19530")
        
        # 尝试删除现有集合（如果存在）
        from pymilvus import utility
        if utility.has_collection(collection_name):
            print(f"删除现有集合 {collection_name}")
            utility.drop_collection(collection_name)
        
        # 创建新集合
        return create_milvus_collection(collection_name)
        
    except Exception as e:
        print(f"重新创建集合失败: {e}")
        return False
    finally:
        connections.disconnect("default")

if __name__ == "__main__":
    # 创建正确的集合
    success = recreate_collection_with_correct_schema()
    if success:
        print("Milvus集合创建成功")
    else:
        print("Milvus集合创建失败")
