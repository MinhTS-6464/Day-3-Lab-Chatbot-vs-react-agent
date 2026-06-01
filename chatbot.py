"""
Lab 3 — Chatbot baseline runner.

Usage:
    python chatbot.py
    python chatbot.py "Your question here"
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Project root on sys.path
sys.path.insert(0, str(ROOT))


def _warn_if_not_using_venv() -> None:
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    venv_python = ROOT / "venv" / "Scripts" / "python.exe"
    if not in_venv and venv_python.is_file():
        print(
            "WARNING: You are not using the project venv.\n"
            "  .\\venv\\Scripts\\activate\n"
            "  python chatbot.py\n"
        )

from dotenv import load_dotenv

from src.chatbot.baseline import ChatbotBaseline
from src.core.factory import create_provider

load_dotenv(ROOT / ".env", override=True)

# Test cases from INSTRUCTOR_GUIDE (e-commerce scenario)
LAB_TEST_CASES = [
    {
        "id": "simple",
        "prompt": "Khách mua 1 củ sạc giá 500.000đ và được giảm 10%. Khách cần trả bao nhiêu tiền?",
        "note": "Chatbot should do well (single-step math).",
    },
    {
        "id": "multi_step",
        "prompt": (
            "Khách muốn mua 2 chiếc iPhone tại cửa hàng CellphoneS, dùng mã giảm giá 'WINNER' "
            "và giao hàng đến Hà Nội. Hãy kiểm tra hàng còn không, áp dụng mã giảm giá, "
            "tính phí vận chuyển và cho biết tổng tiền khách cần thanh toán."
        ),
        "note": "Needs stock + discount + shipping tools — baseline often hallucinates.",
    },
]


def run_case(chatbot: ChatbotBaseline, case: dict) -> None:
    print(f"\n{'=' * 60}")
    print(f"Case [{case['id']}]: {case['note']}")
    print(f"User: {case['prompt']}")
    print("-" * 60)
    answer = chatbot.run(case["prompt"])
    print(f"Assistant:\n{answer}")


def main() -> None:
    _warn_if_not_using_venv()

    try:
        llm = create_provider()
    except Exception as e:
        print(f"Failed to load provider:\n{e}")
        provider = os.getenv("DEFAULT_PROVIDER", "openai")
        print(
            "\nQuick fixes:\n"
            "  - local: activate venv, pip install llama-cpp-python, add .gguf to models/\n"
            "  - openai/google: set a real API key in .env\n"
            f"  Current DEFAULT_PROVIDER={provider!r}"
        )
        sys.exit(1)

    chatbot = ChatbotBaseline(llm)
    print(f"Chatbot baseline | provider={getattr(llm, 'model_name', '?')}")

    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
        print(f"\nUser: {user_prompt}")
        print(chatbot.run(user_prompt))
        return

    for case in LAB_TEST_CASES:
        run_case(chatbot, case)

    print(f"\n{'=' * 60}")
    print("Logs written to logs/ (JSON). Compare with ReAct agent later.")


if __name__ == "__main__":
    main()
