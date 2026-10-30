import time
import logging
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from logging_config import setup_logging
from tools import search_product, check_price

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

llm = ChatAnthropic(model="claude-haiku-4-5-20251001")
tools = [search_product, check_price]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a product assistant. Only use tool results to answer. Never invent prices or product details."
)

def run_agent(user_message: str) -> str:
    start = time.time()
    logger.info(f"Request started: {user_message}")
    try:
        result = agent.invoke({"messages": [HumanMessage(content=user_message)]})
        output = result["messages"][-1].content
        logger.info(f"Request completed in {time.time() - start:.2f}s")
        return output
    except Exception as e:
        logger.error(f"Request failed after {time.time() - start:.2f}s: {e}")
        raise
