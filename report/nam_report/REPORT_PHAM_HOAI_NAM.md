# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Phạm Hoài Nam
- **Student ID**: B21DCCN456
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

In this lab, I was responsible for designing and implementing the **ReAct Agent** architecture, its interaction harness, and resolving platform integration issues.

### 1. Modules Implemented
- **[agent.py](file:///d:/my_project/Day-3-Lab-Chatbot-vs-react-agent/src/agent/agent.py)**: Wrote the complete ReAct logic, the system prompt instruction format, and the dynamic tool execution flow.
- **[openai_provider.py](file:///d:/my_project/Day-3-Lab-Chatbot-vs-react-agent/src/core/openai_provider.py)**: Added intelligent endpoint detection for Xiaomi MiMo Token Plan keys based on prefix parsing.
- **[electronics_tools.py](file:///d:/my_project/Day-3-Lab-Chatbot-vs-react-agent/src/tools/electronics_tools.py)**: Implemented three core sales tools (`search_electronics`, `get_product_detail`, and `calculate_final_price`) with accurate calculations and detailed system descriptions.
- **[main.py](file:///d:/my_project/Day-3-Lab-Chatbot-vs-react-agent/src/main.py)**: Programmed the interactive shell and integrated UTF-8 encoding checks to ensure compatibility with Windows Command Prompt.
- **[logger.py](file:///d:/my_project/Day-3-Lab-Chatbot-vs-react-agent/src/telemetry/logger.py)**: Created `BeautifulConsoleHandler` to intercept JSON logging and print colorized, user-friendly steps on the screen.

### 2. Code Highlights
- **AST-based Safe Arguments Parsing in `ReActAgent`**:
  Instead of using unsafe `eval()` which opens doors for Prompt Injections, I used `ast.literal_eval` wrapped in a mock function signature call to dynamically parse positional and keyword arguments:
  ```python
  # In src/agent/agent.py
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
      logger.error(f"Error parsing args '{args_str}' via ast: {e}")
  ```

---

## II. Debugging Case Study (10 Points)

### 1. Problem Description
Upon starting the interactive session with a query, the application immediately crashed with:
`Error code: 401 - {'error': {'message': 'Missing Authentication header', 'code': 401}}`

### 2. Log Source
From [2026-06-01.log](file:///d:/my_project/Day-3-Lab-Chatbot-vs-react-agent/logs/2026-06-01.log):
```json
{"timestamp": "2026-06-01T15:53:44.236742", "event": "AGENT_START", "data": {"input": "tôi có 35 triệu thì nên mua gì", "model": "xiaomi/mimo-v2.5-pro"}}
```
Followed by the Python Exception stacktrace pointing to `self.client.chat.completions.create`.

### 3. Diagnosis
Xiaomi's MiMo platform issues specialized **Token Plan** subscription keys starting with `tp-` (specifically `tp-s...` representing the Singapore cluster). Standard integrations map the `MiMo-V2.5-Pro` model to OpenRouter endpoints. When OpenRouter received a request with a Xiaomi-specific key, it failed to authenticate it because the key was not registered on the OpenRouter platform, yielding a `401 Unauthorized` status.

### 4. Solution
I updated the client builder in `OpenAIProvider.__init__` to examine the API key's prefix:
```python
if api_key_str.startswith("tp-s"):
    base_url = "https://token-plan-sgp.xiaomimimo.com/v1"
    actual_model = "mimo-v2.5-pro"
```
By redirecting the request to the correct Xiaomi SGP server, authentication succeeded and the agent could query the model correctly.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

### 1. Reasoning
The `Thought` block acts as a scratchpad for the model. Instead of jumping straight to an answer (which forces the model to predict the next word without planning), the `Thought` block lets it break down the question into sub-steps: finding the product first, pulling its price, checking coupons, and only then calculating the final price.

### 2. Reliability
The ReAct Agent can perform *worse* than a standard chatbot if the tool outputs are empty or if the agent enters an infinite loop due to parsing issues (e.g. failing to recognize the `Final Answer:` prefix). Chatbots are more reliable for pure creative writing or simple chit-chat since they don't depend on strict parser formatting.

### 3. Observation
Observations act as external facts. In one trace, when searching for "điện thoại", the tool returned `"Không tìm thấy..."`. The agent read this observation, realized there was no phone in the mock inventory, and adjusted its recommendation to suggest Asus Zenbook and MacBook instead, proving that it can dynamically change its behavior based on environmental feedback.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Move the synchronous tool calls to an asynchronous model (using Python `asyncio`) so the agent can fetch stock prices and specifications in parallel.
- **Safety**: Integrate a "Guardrails" layer (like NeMo Guardrails or Llama Guard) to filter out offensive or off-topic prompts before sending them to the core reasoning loop.
- **Performance**: Move from a local mock catalog to a Vector Database (RAG) with hybrid search (BM25 + Semantic Embeddings) to handle thousands of product SKUs without bloating the prompt size.
