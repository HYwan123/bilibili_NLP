import aiohttp
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import Union, List, Dict, Any, Optional, AsyncGenerator
import json

class AgentClient:
    _instance = None
    # 硬编码 Google API 的配置
    api_key: str = "AIzaSyCZk-v_aHrnoBxEhEHX3MEtEJxyTzGIHwg"  # Google API Key
    model: str = "gemini-3-flash-preview"  # 使用 Google 模型名称

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            # 创建 LangChain Google Generative AI 客户端
            self.google_client = ChatGoogleGenerativeAI(
                model=self.model,
                api_key=SecretStr(self.api_key),
            )

    async def chat(self, messages: List[Dict], model: str = None, system_prompt: str = None) -> Dict[str, Any]:
        # 构建消息列表
        final_messages = []

        # 如果有系统提示词，添加到消息列表开头
        if system_prompt:
            final_messages.append(SystemMessage(content=system_prompt))

        # 添加其余消息
        for msg in messages:
            if msg["role"] == "user":
                final_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                final_messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "system":
                final_messages.append(SystemMessage(content=msg["content"]))

        # 调用 Google Generative AI 模型
        response = self.google_client.invoke(final_messages)
        
        # 将响应格式化为与 OpenAI API 兼容的格式
        content = response.content if response.content is not None else ""
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop"
            }],
            "model": model or self.model,
            "object": "chat.completion"
        }

    async def chat_stream(
        self, messages: List[Dict], model: str = None, system_prompt: str = None
    ) -> AsyncGenerator[str, None]:
        """
        流式AI聊天接口

        Args:
            messages: 消息列表
            model: 模型名称
            system_prompt: 系统提示词

        Yields:
            str: 流式返回的内容片段
        """
        # 构建消息列表
        final_messages = []

        # 如果有系统提示词，添加到消息列表开头
        if system_prompt:
            final_messages.append(SystemMessage(content=system_prompt))

        # 添加其余消息
        for msg in messages:
            if msg["role"] == "user":
                final_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                final_messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "system":
                final_messages.append(SystemMessage(content=msg["content"]))

        # 调用 Google Generative AI 模型的流式功能
        # 使用 sync 迭代而非 async 迭代，因为 LangChain 的 stream 方法返回的是同步迭代器
        response = self.google_client.stream(final_messages)
        for chunk in response:
            content = chunk.content if chunk.content is not None else ""
            if content:
                yield content

    async def one_chat(self, text: str, model: str = None, system_prompt: str = None) -> Dict[str, Any]:
        result = await self.chat(
            messages=[{"role": "user", "content": text or ""}],
            model=model,
            system_prompt=system_prompt
        )
        return result

    async def test(self) -> Dict[str, Any]:
        result = await self.chat(
            messages=[{"role": "user", "content": "test,回复测试成功即可"}]
        )
        return result

    async def close_session(self):
        # Google Generative AI 客户端不需要显式关闭会话
        pass

    @staticmethod
    def make_message(
        messages: List[Dict] = [{"role": "user", "content": "test,回复测试成功即可"}],
        model: str = "gemini-3-flash-preview",
        system_prompt: str = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
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
        messages: List[Dict] = [{"role": "user", "content": "test,回复测试成功即可"}],
        model: str = "gemini-3-flash-preview",
        system_prompt: str = None,
    ) -> Dict[str, Any]:
        """
        创建流式消息payload (已废弃，建议使用 make_message(..., stream=True))
        """
        return AgentClient.make_message(messages=messages, model=model, system_prompt=system_prompt, stream=True)

    @staticmethod
    def get_message_content(response_json: Dict[str, Any]) -> str:
        return response_json["choices"][0]["message"]["content"]

    @staticmethod
    def get_message(response_json: Dict[str, Any]) -> Dict[str, Any]:
        return response_json["choices"][0]["message"]


async def main() -> None:
    print("Google API Key is configured")
    client = AgentClient()
    result = await client.test()
    print(type(result))
    print(result["choices"][0]["message"])
    await client.close_session()


if __name__ == "__main__":
    asyncio.run(main())
