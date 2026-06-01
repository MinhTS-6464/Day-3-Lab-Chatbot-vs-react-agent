import logging
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict

# Ensure utf-8 encoding for console on Windows
if sys.platform.startswith("win") and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

class IndustryLogger:
    """
    Structured logger that simulates industry practices.
    Logs to both console and a file in JSON format.
    """
    def __init__(self, name: str = "AI-Lab-Agent", log_dir: str = "logs"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

class BeautifulConsoleHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            payload = json.loads(msg)
            event = payload.get("event")
            event_data = payload.get("data", {})
            
            CYAN = "\033[96m"
            MAGENTA = "\033[95m"
            GREEN = "\033[92m"
            YELLOW = "\033[93m"
            RESET = "\033[0m"
            BOLD = "\033[1m"
            
            if event == "AGENT_START":
                print(f"\n{CYAN}{BOLD}🤖 Khởi động Agent:{RESET} model={event_data.get('model')}")
            elif event == "AGENT_STEP":
                step = event_data.get("step")
                output = event_data.get("llm_output")
                print(f"\n{MAGENTA}{BOLD}🤔 Suy nghĩ (Bước {step}):{RESET}\n{output}")
            elif event == "TOOL_EXECUTION":
                tool = event_data.get("tool")
                args = event_data.get("args")
                obs = event_data.get("observation")
                print(f"{GREEN}{BOLD}⚙️ Thực thi công cụ:{RESET} {tool}({args})\n{YELLOW}↪ Kết quả:{RESET} {obs}")
            elif event == "AGENT_END":
                steps = event_data.get("steps")
                print(f"\n{CYAN}{BOLD}🏁 Hoàn thành sau {steps} bước.{RESET}")
            else:
                super().emit(record)
        except Exception:
            super().emit(record)

class IndustryLogger:
    """
    Structured logger that simulates industry practices.
    Logs to both console and a file in JSON format.
    """
    def __init__(self, name: str = "AI-Lab-Agent", log_dir: str = "logs"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # File Handler (JSON)
        log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
        file_handler = logging.FileHandler(log_file)
        
        # Console Handler (Beautiful Formatter)
        console_handler = BeautifulConsoleHandler()
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Logs an event with a timestamp and type."""
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event_type,
            "data": data
        }
        self.logger.info(json.dumps(payload))

    def info(self, msg: str):
        self.logger.info(msg)

    def error(self, msg: str, exc_info=True):
        self.logger.error(msg, exc_info=exc_info)

# Global logger instance
logger = IndustryLogger()
