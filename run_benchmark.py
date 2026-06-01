"""
Automated lab benchmark: chatbot baseline vs Agent v1 vs Agent v2.

Usage:
    .\\venv\\Scripts\\activate
    python run_benchmark.py
    python run_benchmark.py --agent-only
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

from src.agent.agent import ReActAgent
from src.agent.agent_v2 import ReActAgentV2
from src.chatbot.baseline import ChatbotBaseline
from src.core.factory import create_provider
from src.tools.electronics_tools import TOOLS_LIST, TOOLS_LIST_V2

TEST_CASES = [
    {
        "id": "simple_math",
        "prompt": "Khách mua 1 củ sạc giá 500.000đ và được giảm 10%. Khách cần trả bao nhiêu tiền?",
    },
    {
        "id": "multi_step_iphone",
        "prompt": (
            "Khách muốn mua 2 chiếc iPhone tại cửa hàng, dùng mã giảm giá 'WINNER' "
            "và giao hàng đến Hà Nội. Kiểm tra hàng, áp mã, tính ship và tổng thanh toán."
        ),
    },
]


def run_benchmark(agent_only: bool = False) -> dict:
    llm = create_provider()
    chatbot = ChatbotBaseline(llm)
    agent_v1 = ReActAgent(llm=llm, tools=TOOLS_LIST, max_steps=5)
    agent_v2 = ReActAgentV2(llm=llm, tools=TOOLS_LIST_V2, max_steps=7)

    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "model": getattr(llm, "model_name", "?"),
        "cases": [],
    }

    for case in TEST_CASES:
        row = {"id": case["id"], "prompt": case["prompt"]}
        print(f"\n=== {case['id']} ===")

        if not agent_only:
            print("  [chatbot]...", flush=True)
            row["chatbot"] = chatbot.run(case["prompt"])[:500]

        print("  [agent_v1]...", flush=True)
        row["agent_v1"] = agent_v1.run(case["prompt"])[:500]

        print("  [agent_v2]...", flush=True)
        row["agent_v2"] = agent_v2.run(case["prompt"])[:500]

        results["cases"].append(row)

    out = ROOT / "report" / "benchmark_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved: {out}")
    print("Logs: logs/ (JSON telemetry)")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-only", action="store_true")
    args = parser.parse_args()
    try:
        run_benchmark(agent_only=args.agent_only)
    except Exception as e:
        print(f"Benchmark failed: {e}")
        sys.exit(1)
