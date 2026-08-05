import os
import json
import urllib.request
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.models.base_model import DeepEvalBaseLLM
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class GeminiJudge(DeepEvalBaseLLM):
    def __init__(self):
        self.model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-3.5-flash-lite")
        self.model = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        res = self.model.invoke(prompt).content
        if isinstance(res, list):
            return "".join([str(p.get("text", p)) if isinstance(p, dict) else str(p) for p in res])
        return str(res)

    async def a_generate(self, prompt: str) -> str:
        res = await self.model.ainvoke(prompt)
        content = res.content
        if isinstance(content, list):
            return "".join([str(p.get("text", p)) if isinstance(p, dict) else str(p) for p in content])
        return str(content)

    def get_model_name(self):
        return self.model_name

test_data = [
    {
        "question": "What is your hourly rate?",
        "ground_truth": "Our hourly work is billed per hour and tracked transparently."
    },
    {
        "question": "How does the fixed price model work?",
        "ground_truth": "It uses an agreed cost upfront. Anything beyond scope is handled by a documented change-order process."
    }
]

def run_evaluation():
    print("Booting DeepEval...")
    judge = GeminiJudge()
    test_cases = []
    
    print("Generating answers for test dataset via live API...")
    for item in test_data:
        print(f"  -> Testing: {item['question']}")
        
        # We query the running FastAPI server instead of booting PyTorch locally to avoid Segfaults
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/chat", 
            data=json.dumps({"query": item["question"]}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
        
        context_texts = result.get("metadata", {}).get("context_texts", [])
        
        test_case = LLMTestCase(
            input=item["question"],
            actual_output=result.get("answer", ""),
            retrieval_context=context_texts,
            expected_output=item["ground_truth"]
        )
        test_cases.append(test_case)
    
    faithfulness = FaithfulnessMetric(threshold=0.7, model=judge)
    answer_relevancy = AnswerRelevancyMetric(threshold=0.7, model=judge)
    
    print("\nRunning DeepEval Evaluation...")
    print("-" * 60)
    
    evaluate(test_cases, [faithfulness, answer_relevancy])

if __name__ == "__main__":
    run_evaluation()
