import mysql.connector
from mysql.connector import errorcode
from passlib.context import CryptContext
from typing import List, Dict, Any
import json
import redis

# --- Configuration ---
DB_CONFIG = {
    'user': 'wan',
    'password': 'Qqwe123123',
    'host': '192.168.2.118',
    'database': 'bilibili_NLP',
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Password Hashing ---
def get_password_hash(password):
    return pwd_context.hash(password)

# --- Database Connection ---
def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

# --- User Management Functions ---
def get_user_by_username(username: str):
    """Fetches a single user from the database by their username."""
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return user

def get_user_report():
    """Fetches all user reports from the database."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)  # dictionary=True 返回字典格式结果
        query = "SELECT * FROM report_history"  # 或你需要的字段
        cursor.execute(query)
        results = cursor.fetchall()  # 读取全部结果，返回列表
    finally:
        cursor.close()
        conn.close()

    return results



def create_user(username: str, password: str):
    """Creates a new user in the database."""
    conn = get_db_connection()
    if not conn:
        return False # Indicates failure
        
    cursor = conn.cursor()
    hashed_password = get_password_hash(password)
    query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    
    try:
        cursor.execute(query, (username, hashed_password))
        conn.commit()
        return True # Indicates success
    except mysql.connector.Error as err:
        print(f"Failed to create user: {err}")
        conn.rollback()
        return False # Indicates failure
    finally:
        cursor.close()
        conn.close()



def add_report_history(uid: int):
    """Adds a BV search to the user's history."""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO report_history (uid)
            VALUES (%s)
        """
        
        cursor.execute(query, (uid,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Failed to insert report history: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# --- History Management Functions ---

def add_bv_history(bv: str, username: str, data: str = "BV comment query"):
    """Adds a BV search to the user's history."""
    conn = get_db_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    
    # Check if BV_history table has a data column
    try:
        cursor.execute("DESCRIBE BV_history")
        columns = [column[0] for column in cursor.fetchall()]  # type: ignore # Use index access for non-dictionary cursor
        has_data_column = 'data' in columns
        
        if has_data_column:
            # Use ON DUPLICATE KEY UPDATE to insert or update the timestamp and data
            query = """
                INSERT INTO BV_history (BV, user, time, data) 
                VALUES (%s, %s, NOW(), %s) 
                ON DUPLICATE KEY UPDATE time = NOW(), user = %s, data = %s
            """
            cursor.execute(query, (bv, username, data, username, data))
        else:
            # Fallback to original query without data column
            query = """
                INSERT INTO BV_history (BV, user, time) 
                VALUES (%s, %s, NOW()) 
                ON DUPLICATE KEY UPDATE time = NOW(), user = %s
            """
            cursor.execute(query, (bv, username, username))
            
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Failed to add BV history: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def add_uuid_history(uid: int|str, username: str, job_id: str, data: str = "User profile query"):
    """Adds a UID search to the user's history, now including job_id."""
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    # Use ON DUPLICATE KEY UPDATE to insert or update the record
    query = """
        INSERT INTO uuid_history (uuid, user, time, data, job_id) 
        VALUES (%s, %s, NOW(), %s, %s) 
        ON DUPLICATE KEY UPDATE time = NOW(), user = %s, data = %s, job_id = %s
    """
    try:
        cursor.execute(query, (uid, username, data, job_id, username, data, job_id))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Failed to add UID history: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def get_bv_history(username: str):
    """Fetches BV search history for a user."""
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    query = "SELECT BV, time FROM BV_history WHERE user = %s ORDER BY time DESC"
    try:
        cursor.execute(query, (username,))
        history = cursor.fetchall()
        return history
    except mysql.connector.Error as err:
        print(f"Failed to get BV history: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_uuid_history(username: str):
    """Fetches UID search history for a user, now including job_id."""
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    # Select the columns as defined in your provided schema, including job_id
    query = "SELECT uuid, user, time, data, job_id FROM uuid_history WHERE user = %s ORDER BY time DESC"
    try:
        cursor.execute(query, (username,))
        history = cursor.fetchall()
        # Convert datetime objects to string for JSON serialization
        for item in history:
            if 'time' in item and hasattr(item['time'], 'isoformat'): # type: ignore
                item['time'] = item['time'].isoformat() # type: ignore
        return history
    except mysql.connector.Error as err:
        print(f"Failed to get UID history: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_history_by_user(user_id: int):
    conn = get_db_connection()
    if not conn: return {"bv_history": [], "uuid_history": []}
    
    # Use dictionary=True to get rows as dicts
    cursor = conn.cursor(dictionary=True)
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    try:
        # First, get the username from user_id
        cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        user_result = cursor.fetchone()
        if not user_result:
            return {"bv_history": [], "uuid_history": []}
        
        username = user_result['username'] # type: ignore
        
        # Fetch BV history - using username instead of user_id
        # Check if BV_history table has a data column
        cursor.execute("DESCRIBE BV_history")
        columns = [column['Field'] for column in cursor.fetchall()] # type: ignore
        has_data_column = 'data' in columns
        
        if has_data_column:
            cursor.execute("SELECT BV as bv, time as query_time, data FROM BV_history WHERE user = %s ORDER BY time DESC", (username,)) # type: ignore
        else:
            cursor.execute("SELECT BV as bv, time as query_time FROM BV_history WHERE user = %s ORDER BY time DESC", (username,)) # type: ignore
        bv_history = cursor.fetchall()

        # Fetch UID history - using username instead of user_id
        cursor.execute("SELECT uuid as uid, job_id, time as query_time FROM uuid_history WHERE user = %s ORDER BY time DESC", (username,)) # type: ignore
        uuid_history = cursor.fetchall()
        
        bv_history = [dict(row) for row in bv_history] # type: ignore
        uuid_history = [dict(row) for row in uuid_history] # type: ignore
        # 为每条uuid_history补充sample_comments
        for item in uuid_history:
            item['sample_comments'] = [] # type: ignore
            job_id = item.get('job_id') # type: ignore
            if job_id:
                # 先查 job_status:{job_id}，再查 {uid}_result
                redis_keys = [f"job_status:{job_id}", f"{item['uid']}_result", f"analysis_{item['uid']}"] # type: ignore
                for key in redis_keys:
                    data = redis_client.get(key)
                    if data:
                        try:
                            result = json.loads(data) # type: ignore
                            sc = result.get('sample_comments')
                            if isinstance(sc, list):
                                item['sample_comments'] = sc # type: ignore
                                break
                        except Exception:
                            continue
        # Convert datetime objects to string for JSON serialization
        from datetime import datetime
        for item in bv_history:
            if isinstance(item, dict) and 'query_time' in item:
                if isinstance(item['query_time'], datetime): # type: ignore
                    item['query_time'] = item['query_time'].isoformat() # type: ignore
        for item in uuid_history:
            if isinstance(item, dict) and 'query_time' in item:
                if isinstance(item['query_time'], datetime): # type: ignore
                    item['query_time'] = item['query_time'].isoformat() # type: ignore

    except mysql.connector.Error as err:
        print(f"Failed to get history by user: {err}")
        return {"bv_history": [], "uuid_history": []}
    finally:
        cursor.close()
        conn.close()
        
    return {"bv_history": bv_history, "uuid_history": uuid_history}

def save_user_comments(uid: int, username: str, comments: List[Dict[str, Any]]) -> bool:
    """
    保存用户评论到数据库
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # 首先检查是否存在user_comments表，如果不存在则创建
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_comments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                uid INT NOT NULL,
                username VARCHAR(255) NOT NULL,
                comment_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_uid (uid),
                INDEX idx_username (username)
            )
        """)
        
        # 删除该用户之前的评论数据（可选，取决于是否需要保留历史）
        cursor.execute("DELETE FROM user_comments WHERE uid = %s", (uid,))
        
        # 插入新的评论数据
        for comment in comments:
            comment_text = comment.get('comment_text', '')
            if comment_text:
                cursor.execute(
                    "INSERT INTO user_comments (uid, username, comment_text) VALUES (%s, %s, %s)",
                    (uid, username, comment_text)
                )
        
        conn.commit()
        print(f"成功保存 {len(comments)} 条评论到数据库，UID: {uid}")
        return True
        
    except mysql.connector.Error as err:
        print(f"保存用户评论失败: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_comments(uid: int|str) -> List[Dict[str, Any]]:
    """
    从数据库获取用户评论
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "SELECT comment_text FROM user_comments WHERE uid = %s ORDER BY created_at DESC",
            (uid,)
        )
        comments = cursor.fetchall()
        
        # 转换为标准格式
        result = [{'comment_text': comment['comment_text']} for comment in comments] # type: ignore
        return result
        
    except mysql.connector.Error as err:
        print(f"获取用户评论失败: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

