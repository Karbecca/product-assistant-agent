import time
import anthropic
import logging
from dotenv import load_dotenv
from logging_config import setup_logging
from tools import search_product, check_price

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5-20251001"
SYSTEM = "You are a product assistant. Only use tool results to answer. Never invent prices or product details."

TOOLS = [
    {
        "name": "search_product",
        "description": "Search the product catalogue by name or description.",
        "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
    },
    {
        "name": "check_price",
        "description": "Get the price of a product by its ID.",
        "input_schema": {"type": "object", "properties": {"product_id": {"type": "string"}}, "required": ["product_id"]}
    }
]

TOOL_MAP = {"search_product": search_product, "check_price": check_price}

def run_agent(user_message: str) -> str:
    start = time.time()
    logger.info(f"Request started: {user_message}")
    messages = [{"role": "user", "content": user_message}]

    try:
        while True:
            response = client.messages.create(
                model=MODEL, max_tokens=1024, system=SYSTEM, tools=TOOLS, messages=messages
            )

            if response.stop_reason == "end_turn":
                result = next(b.text for b in response.content if hasattr(b, "text"))
                logger.info(f"Request completed in {time.time() - start:.2f}s")
                return result

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    logger.info(f"Tool call: {block.name}({block.input})")
                    try:
                        output = TOOL_MAP[block.name](**block.input)
                    except Exception as e:
                        logger.error(f"Tool error {block.name}: {e}")
                        output = f"Tool error: {str(e)}"
                    tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

    except Exception as e:
        logger.error(f"Request failed after {time.time() - start:.2f}s: {e}")
        raise
