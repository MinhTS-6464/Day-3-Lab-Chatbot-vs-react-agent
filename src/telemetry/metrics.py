import time
from typing import Dict, Any, List
from src.telemetry.logger import logger

# USD per 1K tokens (lab estimates — MiMo via API, local ~free)
PRICING_PER_1K = {
    "mimo-v2.5-pro": {"input": 0.0003, "output": 0.0012},
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
    "local": {"input": 0.0, "output": 0.0},
}


class PerformanceTracker:
    """
    Tracking industry-standard metrics for LLMs.
    """

    def __init__(self):
        self.session_metrics = []

    def track_request(self, provider: str, model: str, usage: Dict[str, int], latency_ms: int):
        metric = {
            "provider": provider,
            "model": model,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "latency_ms": latency_ms,
            "cost_estimate": self._calculate_cost(model, usage),
        }
        self.session_metrics.append(metric)
        logger.log_event("LLM_METRIC", metric)

    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        model_key = (model or "").lower()
        rates = PRICING_PER_1K.get("local")
        for key, price in PRICING_PER_1K.items():
            if key in model_key:
                rates = price
                break
        if rates is None:
            rates = {"input": 0.001, "output": 0.002}
        prompt = usage.get("prompt_tokens", 0)
        completion = usage.get("completion_tokens", 0)
        return (prompt / 1000) * rates["input"] + (completion / 1000) * rates["output"]

    def summary(self) -> Dict[str, Any]:
        if not self.session_metrics:
            return {}
        latencies = [m["latency_ms"] for m in self.session_metrics]
        return {
            "calls": len(self.session_metrics),
            "total_tokens": sum(m["total_tokens"] for m in self.session_metrics),
            "total_cost_usd": round(sum(m["cost_estimate"] for m in self.session_metrics), 4),
            "avg_latency_ms": round(sum(latencies) / len(latencies)),
        }


tracker = PerformanceTracker()
