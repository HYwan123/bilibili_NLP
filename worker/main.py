from transformers import pipeline
import asyncio
from redis_client import RedisClientAsync
import json

STREAMS_NAME = "test_streams"

# 使用多语言模型
classifier = pipeline(
    "sentiment-analysis", # type: ignore
    model="nlptown/bert-base-multilingual-uncased-sentiment"
) # type: ignore


async def main() -> None:
    redis_client = RedisClientAsync()
    while True:
        xread_data = await redis_client.get_streams(STREAMS_NAME)
        data = redis_client.get_streams_dict(xread_data)
        id = redis_client.get_streams_id(xread_data)
        bv = data['BV']
        bv_data = await redis_client.get(bv)
        print(json.loads(bv_data))
        for i in json.loads(bv_data):
            print(classifier(i['comment_text']))
            print('\n')
        input()


if __name__ == '__main__':
    asyncio.run(main())