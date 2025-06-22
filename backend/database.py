import mysql.connector
from mysql.connector import errorcode
from passlib.context import CryptContext

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
        columns = [column[0] for column in cursor.fetchall()]  # Use index access for non-dictionary cursor
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

def add_uuid_history(uid: int, username: str, job_id: str, data: str = "User profile query"):
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
            if 'time' in item and hasattr(item['time'], 'isoformat'):
                item['time'] = item['time'].isoformat()
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
    
    try:
        # First, get the username from user_id
        cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        user_result = cursor.fetchone()
        if not user_result:
            return {"bv_history": [], "uuid_history": []}
        
        username = user_result['username']
        
        # Fetch BV history - using username instead of user_id
        # Check if BV_history table has a data column
        cursor.execute("DESCRIBE BV_history")
        columns = [column['Field'] for column in cursor.fetchall()]
        has_data_column = 'data' in columns
        
        if has_data_column:
            cursor.execute("SELECT BV as bv, time as query_time, data FROM BV_history WHERE user = %s ORDER BY time DESC", (username,))
        else:
            cursor.execute("SELECT BV as bv, time as query_time FROM BV_history WHERE user = %s ORDER BY time DESC", (username,))
        bv_history = cursor.fetchall()

        # Fetch UID history - using username instead of user_id
        cursor.execute("SELECT uuid as uid, job_id, time as query_time FROM uuid_history WHERE user = %s ORDER BY time DESC", (username,))
        uuid_history = cursor.fetchall()
        
        # Convert datetime objects to string for JSON serialization
        for item in bv_history:
            if 'query_time' in item and hasattr(item['query_time'], 'isoformat'):
                item['query_time'] = item['query_time'].isoformat()
        for item in uuid_history:
            if 'query_time' in item and hasattr(item['query_time'], 'isoformat'):
                item['query_time'] = item['query_time'].isoformat()

    except mysql.connector.Error as err:
        print(f"Failed to get history by user: {err}")
        return {"bv_history": [], "uuid_history": []}
    finally:
        cursor.close()
        conn.close()
        
    return {"bv_history": bv_history, "uuid_history": uuid_history}

