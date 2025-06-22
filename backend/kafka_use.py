from confluent_kafka import Producer

p = Producer({'bootstrap.servers': '10.0.0.1:9092'})

def acked(err, msg):
    if err is not None:
        print(f"发送失败: {err}")
    else:
        print(f"发送成功: {msg.value()}")

p.produce('test-topic', key='key', value='hello from confluent-kafka', callback=acked)
p.flush()
