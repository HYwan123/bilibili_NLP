import aiohttp
import asyncio
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    api_key: str
    api_host: str


@lru_cache
def get_settings():
    return Settings()  # type: ignore


class OpenaiClient:
    _instance = None
    api_key: str = get_settings().api_key
    api_host: str = get_settings().api_host

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.session_client = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )

    async def chat(self, messages: list[dict], model: str = "kimi-k2", system_prompt: str = None):
        payload = self.make_message(messages=messages, model=model, system_prompt=system_prompt)
        async with self.session_client.post(
            self.api_host, json=payload
        ) as resp:
            return await resp.json()

    async def chat_stream(
        self, messages: list[dict], model: str = "kimi-k2", system_prompt: str = None
    ):
        """
        流式AI聊天接口

        Args:
            messages: 消息列表
            model: 模型名称
            system_prompt: 系统提示词

        Yields:
            str: 流式返回的内容片段
        """
        payload = self.make_message(
            messages=messages, model=model, system_prompt=system_prompt, stream=True
        )

        async with self.session_client.post(self.api_host, json=payload) as resp:
            print(f"Response status: {resp.status}", flush=True)
            print(f"Response headers: {dict(resp.headers)}", flush=True)

            buffer = b""
            async for chunk in resp.content.iter_any():
                buffer += chunk

                # 处理缓冲区中的完整行
                while b"\n" in buffer:
                    line_end = buffer.index(b"\n")
                    line = buffer[:line_end].decode("utf-8").strip()
                    buffer = buffer[line_end + 1 :]

                    print(f"Received line: {line[:100]}", flush=True)

                    if line.startswith("data:"):
                        # 处理 "data:..." 或 "data: ..." 两种情况
                        data = line[5:].lstrip()
                        if data == "[DONE]":
                            print("Received [DONE]", flush=True)
                            return
                        try:
                            import json

                            chunk_data = json.loads(data)

                            # 检查choices和delta
                            if (
                                "choices" in chunk_data
                                and len(chunk_data["choices"]) > 0
                            ):
                                choice = chunk_data["choices"][0]
                                delta = choice.get("delta", {})
                                content = delta.get("content")

                                if content:
                                    print(f"YIELD: {repr(content)}", flush=True)
                                    yield content
                        except json.JSONDecodeError:
                            continue

    async def one_chat(self, text: str, model: str = "kimi-k2", system_prompt: str = None) -> dict:
        payload = self.make_message(
            messages=[{"role": "user", "content": text}],
            model=model,
            system_prompt=system_prompt
        )
        async with self.session_client.post(
            self.api_host,
            json=payload,
        ) as resp:
            return await resp.json()

    async def test(self) -> dict:
        async with self.session_client.post(
            self.api_host, json=self.make_message()
        ) as resp:
            return await resp.json()

    async def close_session(self):
        await self.session_client.close()

    @staticmethod
    def make_message(
        messages: list[dict] = [{"role": "user", "content": "test,回复测试成功即可"}],
        model: str = "kimi-k2",
        system_prompt: str = None,
        stream: bool = False,
    ) -> dict:
        """
        创建消息payload

        Args:
            messages: 消息列表
            model: 模型名称
            system_prompt: 系统提示词，如果提供则添加到消息列表开头
            stream: 是否开启流式输出

        Returns:
            dict: payload
        """
        # 构建消息列表
        final_messages = []

        # 如果有系统提示词，添加到消息列表开头
        if system_prompt:
            final_messages.append({"role": "system", "content": system_prompt})

        # 添加其余消息
        final_messages.extend(messages)

        payload = {
            "model": model,
            "messages": final_messages,
            "stream": stream,
        }

        return payload

    @staticmethod
    def make_message_stream(
        messages: list[dict] = [{"role": "user", "content": "test,回复测试成功即可"}],
        model: str = "kimi-k2",
        system_prompt: str = None,
    ) -> dict:
        """
        创建流式消息payload (已废弃，建议使用 make_message(..., stream=True))
        """
        return OpenaiClient.make_message(messages=messages, model=model, system_prompt=system_prompt, stream=True)

    @staticmethod
    def get_message_content(response_json: dict):
        return response_json["choices"][0]["message"]["content"]

    @staticmethod
    def get_message(response_json: dict):
        return response_json["choices"][0]["message"]


async def main() -> None:
    print(get_settings().api_key)
    client = OpenaiClient()
    result = await client.test()
    print(type(result))
    print(result["choices"][0]["message"])
    await client.close_session()


if __name__ == "__main__":
    asyncio.run(main())
