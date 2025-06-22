import json
import time
import sys
import os

# Add backend directory to sys.path to allow for relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.kafka_producer import KAFKA_TOPIC
from backend import bilibili, sql_use
from kafka import KafkaConsumer

KAFKA_BROKER_URL = 'localhost:9092'

def main():
    print("Starting Kafka consumer...")
    # It's important that group_id is specified so that messages are not re-consumed by the same consumer group
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER_URL,
        auto_offset_reset='earliest', # Start reading at the earliest message if no offset is stored
        group_id='user-analysis-group-1',
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    
    redis_handler = sql_use.SQL_redis()

    for message in consumer:
        try:
            data = message.value
            uid = data['uid']
            job_id = data['job_id']
            
            print(f"Received job {job_id} for UID {uid}. Starting processing...")

            # 1. Update status to "Processing"
            status_update = {"status": "Processing", "progress": 20, "details": f"开始处理用户 {uid} 的分析任务..."}
            redis_handler.set_job_status(job_id, status_update)
            
            # 2. Execute the long-running task
            # This function will need to be modified to accept job_id and update progress internally
            bilibili.user_select(uid, job_id)
            
            # 3. Update status to "Complete"
            print(f"Successfully processed job {job_id} for UID {uid}.")
            final_status = {"status": "Complete", "progress": 100, "details": "分析完成，可以获取结果。"}
            redis_handler.set_job_status(job_id, final_status)

        except KeyError as e:
            print(f"Error processing message, missing key: {e}. Message: {message.value}")
            # We don't have a job_id here if the message is malformed, so we can't update status.
            
        except Exception as e:
            # If we have a job_id, update the status to "Failed"
            if 'job_id' in locals():
                job_id = locals()['job_id']
                print(f"An error occurred while processing job {job_id}: {e}")
                error_status = {"status": "Failed", "progress": -1, "details": f"处理失败: {str(e)}"}
                redis_handler.set_job_status(job_id, error_status)
            else:
                print(f"An error occurred with a message, but no job_id was found: {e}")

if __name__ == "__main__":
    main() 