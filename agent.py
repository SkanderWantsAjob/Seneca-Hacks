# agent_runner.py
import asyncio
import logging
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain.memory import ConversationBufferMemory

from agent_tools import GetReadyHighlightsTool, AgentPublishTool
from firebase_setup import get_user_id_from_token
from firebase_admin import auth
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PublishingAgent")

def create_publishing_agent(llm, tools):
    """Factory to create an LLM agent with memory and tools."""
    prompt = hub.pull("hwchase17/react")
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)

async def process_user(publishing_agent, user_id):
    """Extract and publish highlights for a specific premium user."""
    task_prompt = (
        f"Find all pending video highlights for user {user_id}. "
        f"Return them as structured JSON with [video_id, highlight_timestamps]. "
        f"Then publish each highlight to 'youtube'."
    )
    logger.info(f"Processing highlights for {user_id}")
    result = await publishing_agent.ainvoke({"input": task_prompt})
    logger.info(f"Publishing result for {user_id}: {result}")
    return result

async def agent_loop():
    """Main loop: fetch all premium users and process them."""
    # 🔑 Use DeepSeek via OpenRouter
    llm = ChatOpenAI(
        model="deepseek/deepseek-chat",
        temperature=0.3,
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    tools = [GetReadyHighlightsTool(), AgentPublishTool()]
    publishing_agent = create_publishing_agent(llm, tools)

    while True:
        try:
            premium_users = []
            for user in auth.list_users().iterate_all():
                if user.custom_claims and user.custom_claims.get("premium", False):
                    premium_users.append(user.uid)

            logger.info(f"Found {len(premium_users)} premium users.")

            tasks = [process_user(publishing_agent, uid) for uid in premium_users]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for uid, res in zip(premium_users, results):
                if isinstance(res, Exception):
                    logger.error(f"Error for user {uid}: {res}")
                else:
                    logger.info(f"Successfully processed highlights for {uid}")

        except Exception as e:
            logger.error(f"Critical error in agent loop: {e}")

        await asyncio.sleep(300)  # Wait 5 minutes before next cycle

if __name__ == "__main__":
    asyncio.run(agent_loop())
