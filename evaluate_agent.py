from dotenv import load_dotenv
from anthropic import Anthropic
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase
from deepeval.models.base_model import DeepEvalBaseLLM
from agent import run_agent
from tools import search_product, check_price

load_dotenv()

class ClaudeHaiku(DeepEvalBaseLLM):
    def __init__(self):
        self.client = Anthropic()

    def load_model(self):
        return self.client

    def generate(self, prompt: str, schema=None) -> str:
        response = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    async def a_generate(self, prompt: str, schema=None) -> str:
        return self.generate(prompt)

    def get_model_name(self) -> str:
        return "claude-haiku-4-5-20251001"

eval_model = ClaudeHaiku()

inputs = [
    ("What is the price of P002?", [check_price.invoke({"product_id": "P002"})]),
    ("Find the laptop", [search_product.invoke({"query": "laptop"})]),
    ("What is the price of P999?", [check_price.invoke({"product_id": "P999"})]),
]

test_cases = [
    LLMTestCase(input=inp, actual_output=run_agent(inp), retrieval_context=ctx)
    for inp, ctx in inputs
]

metrics = [
    AnswerRelevancyMetric(threshold=0.7, model=eval_model),
    FaithfulnessMetric(threshold=0.7, model=eval_model),
]

evaluate(test_cases, metrics)
