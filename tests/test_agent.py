from app.utils.agent.agent_client import AgentClient
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, AnyMessage

def test_type():
    import asyncio
    async def run_test():
        agent = AgentClient()
        messages = [{"role": "user", "content": "你好"}]
        result = await agent.chat(messages)
        print(result)
        return result
    return asyncio.run(run_test())

if __name__ == "__main__":
    test_type()
