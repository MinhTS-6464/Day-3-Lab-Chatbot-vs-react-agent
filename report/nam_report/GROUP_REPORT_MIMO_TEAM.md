# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: MiMo Team
- **Team Members**: Nguyễn Nghiệp Minh, Phạm Hoài Nam
- **Deployment Date**: 2026-06-01

---

## 1. Executive Summary

Our project implements an intelligent, production-ready ReAct Agent specializing in electronic products consulting (tư vấn mua sắm đồ điện tử). 
- **Success Rate**: 90% (evaluated on 10 diverse shopping scenarios ranging from general product queries to complex multi-step discount/tax calculations).
- **Key Outcome**: The baseline chatbot frequently failed to answer queries requiring precise price calculation (hallucinating discount values) or exact real-time inventory checking. In contrast, our ReAct Agent achieved 90% accuracy by dynamically selecting and combining `search_electronics`, `get_product_detail`, and `calculate_final_price` tools to output verified data.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation
The agent follows a standard **Thought -> Action -> Observation** cycle, implemented in [agent.py](file:///d:/my_project/Day-3-Lab-Chatbot-vs-react-agent/src/agent/agent.py):
1. **Thought**: The model plans the next logical step based on the prompt history.
2. **Action**: The model outputs a single-line call like `Action: tool_name(arguments)`. We parse this command using Python's `ast` library to ensure safe, type-correct arguments extraction.
3. **Observation**: The engine executes the tool, logs performance metrics, and appends the result (`Observation: <result>`) back into the model's history for the next iteration.
4. **Final Answer**: Once the reasoning is completed, the agent outputs the final response prefixed with `Final Answer:`.

```
     +------------------------------------------------+
     |                  User Input                    |
     +------------------------------------------------+
                             |
                             v
+--->+------------------------------------------------+
|    |           LLM Thought Generation               |
|    +------------------------------------------------+
|                            |
|                            v
|    +------------------------------------------------+
|    |      Is there an Action or Final Answer?       |
|    +------------------------------------------------+
|         /                                      \
|     (Action)                             (Final Answer)
|       /                                          \
|      v                                            v
|  +--------------------------+              +--------------+
|  | Execute Custom Tool      |              | Print Answer |
|  +--------------------------+              +--------------+
|              |
|              v
|  +--------------------------+
|  | Append Tool Observation  |
|  +--------------------------+
|              |
+--------------+
```

### 2.2 Tool Definitions (Inventory)

Our agent is equipped with 3 specialized sales assistance tools implemented in [electronics_tools.py](file:///d:/my_project/Day-3-Lab-Chatbot-vs-react-agent/src/tools/electronics_tools.py):

| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `search_electronics` | `query: str` | Search for electronic products in the catalog by keywords or category (e.g. laptop, smartphone). |
| `get_product_detail` | `product_name: str` | Retrieve technical specs, original price, stock, and summaries of customer reviews (pros/cons) for a specific product. |
| `calculate_final_price` | `price: float, discount_code: str` | Applies coupon codes (e.g. `MIMO10`, `WELCOME50`) and calculates the final cost including 10% VAT. |

### 2.3 LLM Providers Used
- **Primary**: `MiMo-V2.5-Pro` (Xiaomi's Mixture-of-Experts 1.02T parameter model, hosted via the Xiaomi MiMo Open Platform).
- **Secondary (Backup)**: `Gemini 1.5 Flash` (configured as fallback LLM Provider).

---

## 3. Telemetry & Performance Dashboard

Data gathered from real runs logged in the `logs/` directory:

- **Average Latency (P50)**: 14.4 seconds (14,427 ms for single step response).
- **Max Latency (P99)**: 23.2 seconds (23,225 ms during complex multi-step reasoning).
- **Average Tokens per Task**: ~1,100 tokens.
- **Total Cost of Test Suite**: $0.024 (derived from Token Plan billing).

---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study: 401 Unauthorized (Missing Authentication Header)
- **Input**: "tôi có 35 triệu thì nên mua gì"
- **Observation**: The CLI crashed during startup, returning:
  `Error code: 401 - {'error': {'message': 'Missing Authentication header', 'code': 401}}`
- **Root Cause**: The API key `tp-s53cpwgzz...` belongs to the Xiaomi MiMo Token Plan (Singapore cluster). However, the baseline provider was hardcoded to OpenRouter. Sending a Xiaomi cluster key to the OpenRouter gateway caused authentication failure.
- **Solution**: We modified [openai_provider.py](file:///d:/my_project/Day-3-Lab-Chatbot-vs-react-agent/src/core/openai_provider.py) to automatically inspect the API key prefix. Keys starting with `tp-s` are now dynamically routed to `https://token-plan-sgp.xiaomimimo.com/v1`, resolving the 401 error.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2
- **Diff**: In Prompt v2, we added explicit guidelines: *"Không thêm bất cứ ký tự nào khác ngoài định dạng trên khi gọi công cụ. Đối số dạng chuỗi phải nằm trong dấu ngoặc kép. Đối số dạng số thì viết trực tiếp."*
- **Result**: Reduced AST parsing errors from 25% down to 0% by forcing the LLM to output valid python syntax arguments.

### Experiment 2: Chatbot vs Agent
| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| **"Tôi muốn mua Asus Zenbook 14, tính giá có mã MIMO10"** | Bịa ra giá gốc (ví dụ: 25 triệu) và tính toán sai thuế suất. | Gọi `get_product_detail` để lấy giá chính xác (22 triệu) và `calculate_final_price` để xuất hóa đơn chuẩn. | **Agent** |
| **"Cửa hàng có mấy con iPhone?"** | Trả lời chung chung: "Cửa hàng có nhiều loại iPhone..." | Gọi `search_electronics` và báo chính xác số lượng tồn kho (5 cái iPhone 15 Pro Max). | **Agent** |

---

## 6. Production Readiness Review

- **Security**: The arguments are parsed using `ast.literal_eval` instead of `eval`, which prevents arbitrary code execution vulnerabilities from malicious or hallucinated inputs.
- **Guardrails**: The agent has a hard step limit (`max_steps = 5`) to prevent infinite reasoning loops and runaway API costs.
- **Scaling**: For production scaling, we recommend replacing the mock dictionaries in `electronics_tools.py` with a PostgreSQL database and a Vector Database (RAG) for semantic search of items.
