from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from typing import List, Dict
from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph
from langchain.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    AIMessageChunk,
    ToolMessage,
)
import logging
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import SecretStr

class WanAgent:
    """主agent,可调用爬虫爬取newspace的数据"""

    memory_state: InMemorySaver
    agent: CompiledStateGraph
    tools: List[BaseTool]
    memory: Dict[int, List]  # 用户id和对应的记忆内容

    def __init__(self) -> None:
        """初始化创建agent"""
        model = WanAgent.create_llm()
        self.memory_state = InMemorySaver()
        self.agent = WanAgent.create_wan_agent(model, self.memory_state)
        self.memory = {}

    @staticmethod
    def create_llm() -> ChatOpenAI:
        """创建ChatModel"""
        model = ChatOpenAI(
            model="deepseek-v4-flash",
            base_url="https://api.deepseek.com",
            api_key=SecretStr(""),
        )
        return model


    


    @staticmethod
    def create_wan_agent(
        model: ChatOpenAI, 
        memory: InMemorySaver, 
    ) -> CompiledStateGraph:
        """创建agent"""
        agent = create_agent(
            model=model,
            #system_prompt="",
            checkpointer=memory,
        )
        return agent

    async def chat_with_agent(self, input: dict):
        """不带记忆的chat函数,可用于测试"""
        return await self.agent.ainvoke(input)

    async def delete_memory(self, userid: str):
        self.memory_state.delete_thread(userid)


    async def stream_chat(self, userid: int, input: str):
        """带记忆的流式输出异步chat函数"""
        ai_messgae = ""
        async for chunk in self.agent.astream(
            {"messages": input},
            {"configurable": {"thread_id": userid}},
            stream_mode="messages",
            version="v2",
        ):
            msg, metadata = chunk["data"]
            ai_messgae += msg.content  # type: ignore
            print(chunk)
            yield msg.content  # type: ignore
