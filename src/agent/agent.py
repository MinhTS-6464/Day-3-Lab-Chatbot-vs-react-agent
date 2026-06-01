import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        System prompt that instructs the agent to follow ReAct in Vietnamese.
        """
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""Bạn là một trợ lý bán hàng đồ điện tử thông minh, hữu ích và trung thực. Bạn có nhiệm vụ tư vấn sản phẩm, cung cấp chi tiết kỹ thuật và tính toán giá tiền cho khách hàng bằng Tiếng Việt.
Bạn có quyền truy cập vào các công cụ sau:
{tool_descriptions}

Quy trình suy luận và hành động bắt buộc của bạn:
1. Đọc yêu cầu của người dùng.
2. Suy nghĩ (Thought) về bước tiếp theo cần làm để giải quyết yêu cầu.
3. Nếu cần thông tin hoặc thực hiện hành động, hãy gọi công cụ (Action) bằng đúng định dạng sau trên một dòng riêng biệt:
   Action: ten_cong_cu(tham_so)
   Ví dụ:
   Action: search_electronics(query="laptop OLED")
   Action: get_product_detail(product_name="iPhone 15 Pro Max")
   Action: calculate_final_price(price=30000000.0, discount_code="MIMO10")
   
   LƯU Ý: Không thêm bất cứ ký tự nào khác ngoài định dạng trên khi gọi công cụ. Đối số dạng chuỗi phải nằm trong dấu ngoặc kép. Đối số dạng số thì viết trực tiếp.
4. Hệ thống sẽ trả lại kết quả (Observation).
5. Lặp lại Thought và Action nếu bạn cần thêm thông tin.
6. Khi đã có đủ thông tin để trả lời khách hàng, bạn PHẢI viết:
   Final Answer: [câu trả lời hoàn chỉnh, chi tiết và thân thiện của bạn bằng tiếng Việt]

Hãy bắt đầu suy luận!
"""

    def run(self, user_input: str) -> str:
        """
        ReAct loop implementation.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        from src.telemetry.metrics import tracker
        
        conversation_history = f"User: {user_input}\n"
        steps = 0
        final_answer = ""

        while steps < self.max_steps:
            response = self.llm.generate(conversation_history, system_prompt=self.get_system_prompt())
            
            # Track LLM request performance
            tracker.track_request(
                provider=response.get("provider", "openai"),
                model=self.llm.model_name,
                usage=response.get("usage", {}),
                latency_ms=response.get("latency_ms", 0)
            )
            
            content = response.get("content", "").strip()
            logger.log_event("AGENT_STEP", {"step": steps + 1, "llm_output": content})
            
            # Append LLM's thought/action to history
            conversation_history += f"\n{content}"
            
            # Check for Final Answer
            final_answer_match = re.search(r"Final Answer:\s*(.*)", content, re.DOTALL | re.IGNORECASE)
            if final_answer_match:
                final_answer = final_answer_match.group(1).strip()
                break
            
            # Check for Action
            action_match = re.search(r"Action:\s*(\w+)\((.*?)\)", content, re.IGNORECASE)
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_args = action_match.group(2).strip()
                
                # Execute tool
                observation = self._execute_tool(tool_name, tool_args)
                logger.log_event("TOOL_EXECUTION", {"tool": tool_name, "args": tool_args, "observation": observation})
                
                # Append Observation
                conversation_history += f"\nObservation: {observation}"
            else:
                # If LLM didn't call action or provide final answer
                if "Thought:" in content:
                    prompt_correction = "\nSystem: Bạn đã viết Thought nhưng chưa gọi Action hoặc chưa đưa ra Final Answer. Hãy thực hiện Action hoặc đưa ra Final Answer."
                    conversation_history += prompt_correction
                else:
                    # Fallback
                    final_answer = content
                    break
            
            steps += 1
            
        if not final_answer:
            final_answer = "Rất tiếc, tôi không thể hoàn thành yêu cầu trong giới hạn số bước suy nghĩ."
            
        logger.log_event("AGENT_END", {"steps": steps, "final_answer": final_answer})
        return final_answer

    def _parse_action_args(self, args_str: str) -> Dict[str, Any]:
        """
        Parse tool arguments safely using ast.literal_eval.
        """
        import ast
        import json
        
        args_str = args_str.strip()
        if not args_str:
            return {"args": [], "kwargs": {}}
            
        # Try JSON first
        try:
            parsed = json.loads(args_str)
            if isinstance(parsed, dict):
                return {"args": [], "kwargs": parsed}
        except Exception:
            pass
            
        # Try ast.parse by wrapping in a mock function call
        try:
            tree = ast.parse(f"func({args_str})")
            call_node = tree.body[0].value
            kwargs = {}
            args = []
            for kw in call_node.keywords:
                kwargs[kw.arg] = ast.literal_eval(kw.value)
            for arg in call_node.args:
                args.append(ast.literal_eval(arg))
            return {"args": args, "kwargs": kwargs}
        except Exception as e:
            logger.error(f"Error parsing args '{args_str}' via ast: {e}", exc_info=False)
            # Fallback: treat whole string as single string argument
            return {"args": [args_str.strip("\"'")], "kwargs": {}}

    def _execute_tool(self, tool_name: str, args_str: str) -> str:
        """
        Helper method to execute tools by name.
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                func = tool.get('func')
                if not func:
                    return f"Lỗi: Công cụ {tool_name} không có hàm thực thi."
                
                parsed = self._parse_action_args(args_str)
                args = parsed.get("args", [])
                kwargs = parsed.get("kwargs", {})
                
                try:
                    if kwargs:
                        return func(**kwargs)
                    else:
                        return func(*args)
                except Exception as e:
                    return f"Lỗi thực thi công cụ {tool_name}: {str(e)}"
        return f"Công cụ {tool_name} không tồn tại."
