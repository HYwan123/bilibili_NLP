from pymilvus import connections, utility, Collection, CollectionSchema, FieldSchema, DataType
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any

# --- Configuration ---
MILVUS_HOST = 'localhost'
MILVUS_PORT = '19530'
COLLECTION_NAME = 'user_comments'
VECTOR_DIM = 384  # Based on the chosen model: all-MiniLM-L6-v2
MODEL_NAME = 'all-MiniLM-L6-v2'

# --- Load Model ---
# This might take a moment on first run as it downloads the model
print("Loading sentence-transformer model...")
try:
    model = SentenceTransformer(MODEL_NAME)
    print("Sentence-transformer model loaded successfully.")
except Exception as e:
    print(f"Failed to load sentence-transformer model: {e}")
    model = None

# --- Milvus Connection and Setup ---
def connect_to_milvus():
    """Establishes connection to the Milvus server."""
    try:
        connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
        print(f"Successfully connected to Milvus at {MILVUS_HOST}:{MILVUS_PORT}")
    except Exception as e:
        print(f"Failed to connect to Milvus: {e}")
        return False
    return True

def has_collection():
    """Checks if the collection already exists."""
    return utility.has_collection(COLLECTION_NAME)

def create_collection():
    """Creates the Milvus collection with a predefined schema."""
    if has_collection():
        print(f"Collection '{COLLECTION_NAME}' already exists.")
        return Collection(COLLECTION_NAME)

    print(f"Collection '{COLLECTION_NAME}' not found. Creating a new one.")
    fields = [
        FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="user_id", dtype=DataType.INT64, partitions_key=False), # Partitions can be added later if needed
        FieldSchema(name="comment_vector", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM)
    ]
    schema = CollectionSchema(fields, description="User comment vectors")
    collection = Collection(name=COLLECTION_NAME, schema=schema)

    print("Creating IVF_FLAT index for the vector field...")
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="comment_vector", index_params=index_params)
    collection.create_index(field_name="user_id") # Create a scalar index for faster filtering
    print("Indexes created successfully.")
    return collection

def get_collection():
    """Get the collection, creating it if it doesn't exist."""
    if not connections.has_connection("default"):
        if not connect_to_milvus():
            return None
            
    if not has_collection():
        return create_collection()
        
    return Collection(COLLECTION_NAME)

# --- Vector Operations ---
def embed_texts(texts: list[str]) -> np.ndarray:
    """Encodes a list of text strings into vectors."""
    if model is None:
        print("SentenceTransformer model is not loaded. Cannot embed texts.")
        return np.array([])
    return model.encode(texts)

def insert_vectors(user_id: int, vectors: np.ndarray):
    """Inserts vectors for a specific user into the collection."""
    collection = get_collection()
    if not collection or vectors.size == 0:
        print("Could not get collection or vectors are empty. Aborting insertion.")
        return None
        
    entities = [
        {"user_id": user_id, "comment_vector": vector} for vector in vectors
    ]
    
    mr = collection.insert(entities)
    collection.flush()
    print(f"Inserted {len(vectors)} vectors for user_id {user_id}. Primary keys: {mr.primary_keys}")
    return mr

def get_user_vectors(user_id: int) -> np.ndarray:
    """Retrieves all vectors for a given user."""
    collection = get_collection()
    if not collection:
        return np.array([])
        
    collection.load()
    expr = f"user_id == {user_id}"
    results = collection.query(
        expr=expr,
        output_fields=["comment_vector"]
    )
    
    if not results:
        return np.array([])
        
    vectors = [item['comment_vector'] for item in results]
    return np.array(vectors)

def get_user_avg_vector(user_id: int) -> np.ndarray:
    """Calculates the average vector for a given user."""
    vectors = get_user_vectors(user_id)
    if vectors.size == 0:
        print(f"No vectors found for user_id {user_id}. Cannot calculate average.")
        return np.array([])
        
    avg_vector = np.mean(vectors, axis=0)
    print(f"Calculated average vector for user_id {user_id} from {len(vectors)} vectors.")
    return avg_vector

def process_and_store_comments(user_id: int, comments: List[Dict[str, Any]]):
    """
    Extracts text from comments, embeds them, and stores them in Milvus.
    This is the main entry point for processing user comments.
    """
    if not comments:
        print(f"No comments provided for user {user_id}. Nothing to process.")
        return
        
    texts = [comment.get('comment_text') for comment in comments if comment.get('comment_text')]
    
    if not texts:
        print(f"No valid comment texts found in the provided comments for user {user_id}.")
        return

    print(f"Embedding {len(texts)} comments for UID {user_id}...")
    comment_vectors = embed_texts(texts)

    if comment_vectors is not None and comment_vectors.size > 0:
        insert_vectors(user_id=user_id, vectors=comment_vectors)
    else:
        print(f"Vector embedding resulted in no vectors for user {user_id}.") 