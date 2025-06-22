import json
import time
import sys
import os

# Add backend directory to sys.path to allow for relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import bilibili, sql_use

def main():
    print("Starting Redis consumer...")
    redis_handler = sql_use.SQL_redis()
    
    if not redis_handler.redis_client:
        print("Could not connect to Redis. Consumer cannot start.")
        return

    print("Redis consumer started. Waiting for jobs in 'analysis_queue'...")

    while True:
        try:
            # BRPOP is a blocking pop. It will wait until an item is available in the list.
            # The '0' means it will wait indefinitely.
            # It returns a tuple: (list_name, item_bytes)
            source, message_bytes = redis_handler.redis_client.brpop("analysis_queue", 0)
            
            data = json.loads(message_bytes)
            uid = data['uid']
            job_id = data['job_id']
            
            print(f"Received job {job_id} for UID {uid} from Redis queue '{source.decode()}'. Starting processing...")
            # The core logic is now in bilibili.py which handles its own status printing
            bilibili.user_select(uid, job_id) 
        except Exception as e:
            print(f"An error occurred while processing job {job_id}: {e}")
            # Optionally, update job status to Failed if bilibili.user_select didn't handle it
        
        # A small sleep to prevent tight looping in case of continuous errors, though BRPOP handles waiting.
        time.sleep(1)


if __name__ == "__main__":
    main() 