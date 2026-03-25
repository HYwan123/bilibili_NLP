from zai import ZhipuAiClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import asyncio


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # 忽略额外字段
    )

    api_key: str = ""
    # 添加额外字段支持，用于可能的扩展
    base_url: str = ""
    timeout: int = 30


@lru_cache
def get_settings():
    return Settings()  # type: ignore


class OpenaiClient:
    _instance = None
    api_key: str = get_settings().api_key

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.client = ZhipuAiClient(api_key=self.api_key)

    async def chat(self, messages: list[dict], model: str = "glm-4.7-flash", system_prompt: str = None, max_tokens: int = 65536, temperature: float = 1.0):
        """
        同步AI聊天接口 (已包装为异步)

        Args:
            messages: 消息列表
            model: 模型名称
            system_prompt: 系统提示词
            max_tokens: 最大输出 tokens
            temperature: 控制输出的随机性

        Returns:
            Zhipu AI响应对象: AI响应结果
        """
        # 构建完整消息列表
        final_messages = []
        if system_prompt is not None:
            final_messages.append({"role": "system", "content": system_prompt})
        final_messages.extend(messages)

        # 标准化消息格式，确保兼容旧格式和新格式
        standardized_messages = []
        for msg in final_messages:
            role = msg["role"]
            # 确保role不为None，如果为None则使用默认值
            role = role if role is not None else "user"
            content = msg["content"]
            
            # 检查内容是否已经是列表格式（新格式）
            if isinstance(content, list):
                # 如果是列表格式，直接使用
                standardized_messages.append({
                    "role": role,
                    "content": content
                })
            else:
                # 确保内容不为None，如果为None则使用默认值
                content_str = content if content is not None else ""
                # 如果是字符串格式，转换为新格式
                standardized_messages.append({
                    "role": role,
                    "content": [{
                        "type": "text",
                        "text": content_str
                    }]
                })

        # 确保模型参数不为None，如果为None则使用默认值
        model = model if model is not None else "glm-4.7-flash"
        # 使用 asyncio.to_thread 运行同步 SDK 调用，避免阻塞事件循环
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=model,
            messages=standardized_messages
        )

        return response

    async def chat_stream(
        self, messages: list[dict], model: str = "glm-4.7-flash", system_prompt: str = None, max_tokens: int = 65536, temperature: float = 1.0
    ):
        """
        流式AI聊天接口 (已包装为异步)

        Args:
            messages: 消息列表
            model: 模型名称
            system_prompt: 系统提示词
            max_tokens: 最大输出 tokens
            temperature: 控制输出的随机性

        Yields:
            str: 流式返回的内容片段
        """
        # 构建完整消息列表
        final_messages = []
        if system_prompt is not None:
            # 确保system_prompt不为None，如果为None则使用默认值
            system_prompt = system_prompt if system_prompt is not None else "你是一个有用的助手。"
            final_messages.append({"role": "system", "content": system_prompt})
        final_messages.extend(messages)

        # 标准化消息格式，确保兼容旧格式和新格式
        standardized_messages = []
        for msg in final_messages:
            role = msg["role"]
            # 确保role不为None，如果为None则使用默认值
            role = role if role is not None else "user"
            content = msg["content"]
            
            # 检查内容是否已经是列表格式（新格式）
            if isinstance(content, list):
                # 如果是列表格式，直接使用
                standardized_messages.append({
                    "role": role,
                    "content": content
                })
            else:
                # 确保内容不为None，如果为None则使用默认值
                content_str = content if content is not None else ""
                # 如果是字符串格式，转换为新格式
                standardized_messages.append({
                    "role": role,
                    "content": [{
                        "type": "text",
                        "text": content_str
                    }]
                })

        # 确保模型参数不为None，如果为None则使用默认值
        model = model if model is not None else "glm-4.7-flash"
        
        # 使用 asyncio.to_thread 运行同步 SDK 调用
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=model,
            messages=standardized_messages,
            stream=True
        )

        # 流式获取回复 - 使用同步迭代器包装在异步生成器中
        # zai-sdk 的流式响应迭代可能是阻塞的
        it = iter(response)
        
        while True:
            try:
                # 在单独的线程中获取下一个 chunk，避免阻塞主线程
                chunk = await asyncio.to_thread(next, it)
                
                # 检查 chunk 是否为元组格式 (event_type, data) 或其他格式
                if isinstance(chunk, tuple) and len(chunk) >= 2:
                    actual_chunk = chunk[1]
                else:
                    actual_chunk = chunk

                # 对于流式响应，处理实际的 chunk
                if hasattr(actual_chunk, 'choices') and actual_chunk.choices:
                    if hasattr(actual_chunk.choices[0], 'delta') and hasattr(actual_chunk.choices[0].delta, 'content'):
                        content = actual_chunk.choices[0].delta.content
                        if content:
                            yield content
            except StopIteration:
                break
            except Exception as e:
                # 发生错误时跳出循环
                break

    async def one_chat(self, text: str, model: str = "glm-4.7-flash", system_prompt: str = None, max_tokens: int = 65536, temperature: float = 1.0):
        """
        单次AI聊天接口

        Args:
            text: 用户输入文本
            model: 模型名称
            system_prompt: 系统提示词
            max_tokens: 最大输出 tokens
            temperature: 控制输出的随机性

        Returns:
            Zhipu AI响应对象: AI响应结果
        """
        messages = [{"role": "user", "content": text}]
        # 传递参数给chat方法
        return await self.chat(messages=messages, model=model, system_prompt=system_prompt, max_tokens=max_tokens, temperature=temperature)
        """
        单次AI聊天接口

        Args:
            text: 用户输入文本
            model: 模型名称
            system_prompt: 系统提示词
            max_tokens: 最大输出 tokens
            temperature: 控制输出的随机性

        Returns:
            Zhipu AI响应对象: AI响应结果
        """
        messages = [{"role": "user", "content": text}]
        # 传递参数给chat方法，但chat方法内部会根据模型类型决定是否使用这些参数
        return await self.chat(messages=messages, model=model, system_prompt=system_prompt, max_tokens=max_tokens, temperature=temperature)

    async def test(self):
        """
        测试接口
        使用系统提示词确保API调用正确
        """
        # 使用系统提示词和用户消息，确保API调用成功
        system_prompt = "你是一个有用的助手，专门用于测试API连接。"
        messages = [{
            "role": "user", 
            "content": [{
                "type": "text",
                "text": "test,回复测试成功即可"
            }]
        }]
        return await self.chat(messages=messages, system_prompt=system_prompt)

    async def close_session(self):
        """
        关闭会话（zai-sdk 不需要手动关闭）
        """
        pass

    @staticmethod
    def get_message_content(response_json):
        """
        获取响应中的内容
        
        Args:
            response_json: AI响应结果
            
        Returns:
            str: 消息内容
        """
        # 检查是否是同步响应对象
        if hasattr(response_json, 'choices') and response_json.choices:
            if response_json.choices[0].message and hasattr(response_json.choices[0].message, 'content'):
                return response_json.choices[0].message.content or ""
            else:
                # 如果内容为 None，返回空字符串
                return ""
        else:
            # 如果是流式响应，可能需要其他处理方式
            raise TypeError("Response object does not have expected structure for getting content")

    @staticmethod
    def get_message(response_json):
        """
        获取响应中的消息对象
        
        Args:
            response_json: AI响应结果
            
        Returns:
            Message: 消息对象
        """
        # 检查是否是同步响应对象
        if hasattr(response_json, 'choices') and response_json.choices:
            return response_json.choices[0].message
        else:
            # 如果是流式响应，可能需要其他处理方式
            raise TypeError("Response object does not have expected structure for getting message")


async def main() -> None:
    print(get_settings().api_key)
    client = OpenaiClient()
    result = await client.test()
    print(type(result))
    if hasattr(result, 'choices'):
        print(OpenaiClient.get_message(result))
    else:
        print("Response object does not have expected structure for getting message")
    await client.close_session()


if __name__ == "__main__":
    asyncio.run(main())
