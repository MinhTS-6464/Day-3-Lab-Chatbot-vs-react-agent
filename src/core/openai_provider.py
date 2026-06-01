import time
from typing import Dict, Any, Optional, Generator
from openai import OpenAI
from src.core.llm_provider import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None):
        base_url = None
        if model_name == "MiMo-V2.5-Pro":
            # Default to standard Xiaomi MiMo API
            base_url = "https://api.xiaomimimo.com/v1"
            actual_model = "mimo-v2.5-pro"
            
            if api_key:
                api_key_str = api_key.strip()
                if api_key_str.startswith("tp-"):
                    # Xiaomi Token Plan
                    if api_key_str.startswith("tp-s"):
                        base_url = "https://token-plan-sgp.xiaomimimo.com/v1"
                    elif api_key_str.startswith("tp-a") or api_key_str.startswith("tp-e"):
                        base_url = "https://token-plan-ams.xiaomimimo.com/v1"
                    else:
                        base_url = "https://token-plan-cn.xiaomimimo.com/v1"
                elif api_key_str.startswith("sk-or"):
                    # OpenRouter
                    base_url = "https://openrouter.ai/api/v1"
                    actual_model = "xiaomi/mimo-v2.5-pro"
        else:
            actual_model = model_name
        super().__init__(actual_model, api_key)
        self.client = OpenAI(api_key=self.api_key, base_url=base_url)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
        )

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        # Extraction from OpenAI response
        content = response.choices[0].message.content
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }

        return {
            "content": content,
            "usage": usage,
            "latency_ms": latency_ms,
            "provider": "openai"
        }

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
