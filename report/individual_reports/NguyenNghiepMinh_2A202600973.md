# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Nghiệp Minh
- **Student ID**: 2A2026009732A202600973
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

- **`src/chatbot/baseline.py`**, **`chatbot.py`**: Chatbot baseline một lượt LLM + telemetry.
- **`src/core/factory.py`**: Lazy-load provider (openai/MiMo, gemini, local), validate `.env`.
- **`src/agent/agent_v2.py`**: Agent v2 — parser Action cải tiến, prompt có mã giảm, ưu tiên tool.
- **`src/tools/electronics_tools.py`**: Bổ sung `WINNER`, `check_stock`, `calc_shipping`, `TOOLS_LIST_V2`.
- **`run_benchmark.py`**, **`scripts/analyze_logs.py`**: Tự động so sánh chatbot vs agent + tổng hợp metrics.
- **`src/telemetry/metrics.py`**: Ước lượng chi phí theo model (MiMo / local).

**Code highlight**: Agent v2 xử lý Action trước Final Answer trong cùng response — tránh kết thúc sớm khi model gọi tool ở cuối đoạn.

---

## II. Debugging Case Study (10 Points)

- **Problem**: Agent v1 báo mã `WINNER` “không áp dụng” dù khách yêu cầu rõ.
- **Log Source**: `logs/2026-06-01.log` — event `TOOL_EXECUTION`, `"discount_applied": false`
- **Diagnosis**: `PROMO_CODES` chỉ có `MIMO10`, `WELCOME50`; LLM vẫn gọi đúng tool nhưng backend từ chối mã.
- **Solution**: Thêm `WINNER` vào `electronics_tools.py`; cập nhật prompt v2 liệt kê mã hợp lệ; chạy lại → `discount_applied: true` (15%).

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: Khối `Thought` + `Observation` giúp agent “nhớ” giá từ catalog thay vì suy đoán.
2. **Reliability**: Agent chậm hơn và tốn token hơn; câu chào hỏi mơ hồ đôi khi agent v1 trả lời dài không cần tool — chatbot đơn giản hơn.
3. **Observation**: Khi tool trả “mã không hợp lệ”, bước sau model đổi mã hoặc giải thích — đây là feedback vòng ReAct.

**Local vs API**: Phi-3 local rẻ, chậm ~5–23s; MiMo API nhanh hơn từng bước, gọi tool ổn định hơn cho tiếng Việt.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Hàng đợi tool async; cache embedding cho catalog lớn.
- **Safety**: Supervisor LLM kiểm tra Action trước khi thực thi.
- **Performance**: Tool retrieval (chỉ đưa 3 tool liên quan vào prompt).

---

> Submit as `NguyenNghiepMinh_2A202600973.md` in this folder.
