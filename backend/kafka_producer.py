import json
from kafka import KafkaProducer
import atexit

# --- Configuration ---
KAFKA_BROKER_URL = '10.0.0.1:9092'
TOPIC_NAME = 'user_analysis_jobs'
KAFKA_TOPIC = "user-analysis-requests"

# --- Kafka Producer Singleton ---
_producer = None

def get_producer():
    """Initializes and returns a singleton KafkaProducer instance."""
    global _producer
    if _producer is None:
        try:
            _producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER_URL,
                # This serializer will take a dict, convert it to a JSON string, then encode to bytes.
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=5, # Retry sending messages on failure
            )
            print("Kafka producer initialized successfully.")
            # Ensure producer is closed on exit
            atexit.register(close_producer)
        except Exception as e:
            print(f"Failed to initialize Kafka producer: {e}")
            _producer = None
    return _producer

def close_producer():
    """Closes the Kafka producer."""
    global _producer
    if _producer:
        print("Closing Kafka producer...")
        _producer.flush()
        _producer.close()

def send_analysis_request(uid: int, job_id: str) -> bool:
    """
    Sends a user analysis request to the Kafka topic.
    """
    producer = get_producer()
    if producer:
        try:
            message = {
                "uid": uid,
                "job_id": job_id
            }
            # Send the dictionary directly. The value_serializer will handle the conversion.
            producer.send(KAFKA_TOPIC, value=message)
            # The flush is not strictly necessary here on every send, 
            # as the producer batches messages, but can be useful for ensuring it's sent promptly.
            # producer.flush() 
            print(f"Sent analysis request for UID: {uid} with Job ID: {job_id} to topic '{KAFKA_TOPIC}'")
            return True
        except Exception as e:
            print(f"Failed to send message to Kafka: {e}")
            return False
    return False 