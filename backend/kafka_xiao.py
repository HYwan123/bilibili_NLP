from confluent_kafka import Consumer

c = Consumer({
    'bootstrap.servers': '10.0.0.1:9092',
    'group.id': 'dad2',
    'enable.auto.commit': 'true',
    'auto.offset.reset': 'earliest'
})

c.subscribe(['test-topic'])

while True:
    msg = c.poll(11.0)
    if msg is None:
        continue
    if msg.error():
        print(f"错误: {msg.error()}")
        continue
    print(f"收到消息: {msg.value().decode('utf-8')}")
