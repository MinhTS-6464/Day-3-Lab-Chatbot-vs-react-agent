import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure utf-8 encoding for console on Windows
if sys.platform.startswith("win") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Add project root to python path if needed
sys.path.insert(0, str(PROJECT_ROOT))

# Load .env from project root (override Windows env vars if any)
load_dotenv(PROJECT_ROOT / ".env", override=True)

from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActAgent
from src.agent.agent_v2 import ReActAgentV2
from src.tools.electronics_tools import TOOLS_LIST, TOOLS_LIST_V2

def print_banner():
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    print("\n" + "="*60)
    print(f" {CYAN}{BOLD}🖥️  MIMO-V2.5-PRO ELECTRONICS CONSULTING AGENT 🖥️{RESET}")
    print(f" {MAGENTA}Hệ thống tư vấn mua sắm thiết bị điện tử thông minh{RESET}")
    print("="*60)
    print(" Hướng dẫn sử dụng:")
    print(" - Nhập câu hỏi để được tư vấn sản phẩm, thông số hoặc tính giá.")
    print(" - Nhập 'exit' hoặc 'quit' để thoát chương trình.")
    print("="*60 + "\n")

def main():
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key or api_key == "your_openai_api_key_here":
        RED = "\033[91m"
        YELLOW = "\033[93m"
        RESET = "\033[0m"
        env_path = PROJECT_ROOT / ".env"
        print(f"{RED}⚠️ LỖI: OPENAI_API_KEY chưa hợp lệ trong file .env!{RESET}")
        print(f"{YELLOW}1. Mở {env_path}{RESET}")
        print(f"{YELLOW}2. Dán API key MiMo (tp-...) vào OPENAI_API_KEY{RESET}")
        print(f"{YELLOW}3. Lưu file (Ctrl+S) — chỉnh trong editor chưa lưu thì Python không đọc được.{RESET}\n")
        return

    model_name = os.getenv("DEFAULT_MODEL", "MiMo-V2.5-Pro")
    
    try:
        # Initialize OpenAIProvider pointing to OpenRouter for MiMo-V2.5-Pro
        provider = OpenAIProvider(model_name=model_name, api_key=api_key)
        
        agent_version = os.getenv("AGENT_VERSION", "2").strip()
        if agent_version == "1":
            agent = ReActAgent(llm=provider, tools=TOOLS_LIST, max_steps=5)
            print("Agent mode: v1 (baseline ReAct)\n")
        else:
            agent = ReActAgentV2(llm=provider, tools=TOOLS_LIST_V2, max_steps=7)
            print("Agent mode: v2 (improved ReAct + shipping/stock)\n")
        
        print_banner()
        
        GREEN = "\033[92m"
        CYAN = "\033[96m"
        RESET = "\033[0m"
        BOLD = "\033[1m"
        
        while True:
            try:
                user_input = input(f"{GREEN}{BOLD}Khách hàng:{RESET} ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit"]:
                    print(f"\n{CYAN}Cảm ơn quý khách đã sử dụng dịch vụ tư vấn của MiMo Electronics!{RESET}\n")
                    break
                
                # Execute agent run
                final_answer = agent.run(user_input)
                
                # Print final answer beautifully
                print("\n" + "-"*40)
                print(f"{CYAN}{BOLD}💬 Trợ lý (MiMo):{RESET}")
                print(final_answer)
                print("-"*40 + "\n")
                
            except KeyboardInterrupt:
                print(f"\n\n{CYAN}Tạm biệt quý khách!{RESET}\n")
                break
            except Exception as e:
                print(f"\n\033[91m❌ Có lỗi xảy ra trong quá trình xử lý: {e}\033[0m\n")
                
    except Exception as e:
        print(f"\033[91m❌ Không thể khởi tạo Agent: {e}\033[0m")

if __name__ == "__main__":
    main()
