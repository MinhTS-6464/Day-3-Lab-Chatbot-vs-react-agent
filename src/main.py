import os
import sys
from dotenv import load_dotenv

# Ensure utf-8 encoding for console on Windows
if sys.platform.startswith("win") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to python path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActAgent
from src.tools.electronics_tools import TOOLS_LIST

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
    # Load env variables from .env file
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or "your_openai_api_key_here" in api_key:
        RED = "\033[91m"
        YELLOW = "\033[93m"
        RESET = "\033[0m"
        print(f"{RED}⚠️ LỖI: Chưa cấu hình OPENAI_API_KEY trong file .env!{RESET}")
        print(f"{YELLOW}Vui lòng mở file .env và thay thế 'your_openai_api_key_here' bằng API Key thật của bạn.{RESET}\n")
        return

    model_name = os.getenv("DEFAULT_MODEL", "MiMo-V2.5-Pro")
    
    try:
        # Initialize OpenAIProvider pointing to OpenRouter for MiMo-V2.5-Pro
        provider = OpenAIProvider(model_name=model_name, api_key=api_key)
        
        # Initialize ReAct Agent with the custom electronics tools
        agent = ReActAgent(llm=provider, tools=TOOLS_LIST, max_steps=5)
        
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
