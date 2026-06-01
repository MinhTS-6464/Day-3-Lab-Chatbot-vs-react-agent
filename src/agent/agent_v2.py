"""
ReAct Agent v2 — improvements after v1 failure analysis (see logs/ and GROUP_REPORT).

- Lists valid promo codes in prompt
- Processes Action before Final Answer in the same LLM turn
- Requires tools for price/stock/shipping questions
- Retry hint when tool returns invalid discount
"""

import re
from typing import List, Dict, Any

from src.agent.agent import ReActAgent
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger


class ReActAgentV2(ReActAgent):
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 7):
        super().__init__(llm, tools, max_steps=max_steps)
        self.version = 2

    def get_system_prompt(self) -> str:
        tool_descriptions = "\n".join(
            [f"- {t['name']}: {t['description']}" for t in self.tools]
        )
        return f"""Bạn là trợ lý bán hàng điện tử (Tiếng Việt). Luôn dùng công cụ cho giá, tồn kho, mã giảm, vận chuyển — không tự bịa số.

Công cụ:
{tool_descriptions}

Mã giảm giá hợp lệ: MIMO10 (giảm 10%), WELCOME50 (giảm 50.000 VND), WINNER (giảm 15% đơn smartphone).
Nếu khách dùng mã khác, báo không hợp lệ sau khi gọi calculate_final_price.

Quy trình (mỗi lượt chỉ MỘT Action HOẶC Final Answer):
Thought: ...
Action: tool_name(arg="value", number=123)

Sau Observation, lặp lại hoặc kết thúc:
Final Answer: ...

Quy tắc:
- Mỗi Action trên một dòng, bắt đầu bằng "Action:".
- Câu hỏi nhiều bước (tồn kho + giá + ship): gọi lần lượt search_electronics → get_product_detail → calculate_final_price → calc_shipping.
- Không viết Final Answer trong cùng lượt với Action.
- Giá truyền vào calculate_final_price là số float (VD: 60000000.0 cho 2 máy).
"""

    def _extract_action(self, content: str):
        """Return last Action: line in content (handles text before Action)."""
        matches = list(
            re.finditer(r"Action:\s*(\w+)\((.*?)\)\s*$", content, re.IGNORECASE | re.MULTILINE)
        )
        if not matches:
            matches = list(
                re.finditer(r"Action:\s*(\w+)\((.*?)\)", content, re.IGNORECASE | re.DOTALL)
            )
        if not matches:
            return None
        m = matches[-1]
        return m.group(1).strip(), m.group(2).strip()

    def run(self, user_input: str) -> str:
        logger.log_event(
            "AGENT_START",
            {"input": user_input, "model": self.llm.model_name, "version": 2},
        )
        from src.telemetry.metrics import tracker

        conversation_history = f"User: {user_input}\n"
        steps = 0
        final_answer = ""
        tools_used = 0

        while steps < self.max_steps:
            response = self.llm.generate(
                conversation_history, system_prompt=self.get_system_prompt()
            )
            tracker.track_request(
                provider=response.get("provider", "openai"),
                model=self.llm.model_name,
                usage=response.get("usage", {}),
                latency_ms=response.get("latency_ms", 0),
            )

            content = response.get("content", "").strip()
            logger.log_event("AGENT_STEP", {"step": steps + 1, "llm_output": content, "version": 2})
            conversation_history += f"\n{content}"

            action = self._extract_action(content)
            if action:
                tool_name, tool_args = action
                observation = self._execute_tool(tool_name, tool_args)
                tools_used += 1
                logger.log_event(
                    "TOOL_EXECUTION",
                    {"tool": tool_name, "args": tool_args, "observation": observation, "version": 2},
                )
                conversation_history += f"\nObservation: {observation}"
                if '"discount_applied": false' in observation or "Không áp dụng" in observation:
                    conversation_history += (
                        "\nSystem: Mã giảm không hợp lệ. Thử MIMO10 hoặc WINNER, hoặc báo khách trong Final Answer."
                    )
                steps += 1
                continue

            final_answer_match = re.search(
                r"Final Answer:\s*(.*)", content, re.DOTALL | re.IGNORECASE
            )
            if final_answer_match:
                final_answer = final_answer_match.group(1).strip()
                break

            if "Thought:" in content:
                conversation_history += (
                    "\nSystem: Chỉ gọi một Action trên dòng riêng, hoặc Final Answer khi đủ dữ liệu."
                )
            else:
                final_answer = content
                break

            steps += 1

        if not final_answer:
            final_answer = (
                "Rất tiếc, tôi chưa hoàn thành được yêu cầu trong giới hạn bước. "
                "Vui lòng thử lại với tên sản phẩm và mã giảm rõ ràng."
            )

        logger.log_event(
            "AGENT_END",
            {"steps": steps, "tools_used": tools_used, "final_answer": final_answer, "version": 2},
        )
        return final_answer
