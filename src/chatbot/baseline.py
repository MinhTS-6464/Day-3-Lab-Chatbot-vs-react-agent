from typing import List, Optional

from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker


class ChatbotBaseline:
    """
    Minimal chatbot: one LLM call per turn, no tools, no ReAct loop.
    Used as baseline to compare against ReActAgent on multi-step tasks.
    """

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def get_system_prompt(self) -> str:
        return (
            "You are a helpful e-commerce shopping assistant. "
            "Answer the user's question clearly and concisely. "
            "If you lack real-time data (stock, coupons, shipping rates), "
            "say what you would need to know instead of inventing specific numbers."
        )

    def run(self, user_input: str, history: Optional[List[str]] = None) -> str:
        """
        Single-turn (or history-augmented) chat: prompt -> LLM -> reply.
        """
        logger.log_event(
            "CHATBOT_START",
            {"input": user_input, "model": self.llm.model_name},
        )

        prompt = user_input
        if history:
            context = "\n".join(history)
            prompt = f"Previous conversation:\n{context}\n\nUser: {user_input}"

        result = self.llm.generate(prompt, system_prompt=self.get_system_prompt())
        answer = result["content"]

        tracker.track_request(
            provider=result.get("provider", "unknown"),
            model=self.llm.model_name,
            usage=result["usage"],
            latency_ms=result["latency_ms"],
        )

        logger.log_event(
            "CHATBOT_END",
            {
                "answer_preview": answer[:200],
                "latency_ms": result["latency_ms"],
                "total_tokens": result["usage"].get("total_tokens", 0),
            },
        )

        return answer
