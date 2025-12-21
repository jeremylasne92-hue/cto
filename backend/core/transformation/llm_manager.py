import os
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LLMManager:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.local_model_url = self.config.get('LOCAL_MODEL_URL', 'http://localhost:11434/api/generate')
        self.cloud_api_key = self.config.get('CLOUD_API_KEY', os.environ.get('OPENAI_API_KEY'))
        self.cloud_api_url = self.config.get('CLOUD_API_URL', 'https://api.openai.com/v1/chat/completions')
        self.model_name = self.config.get('MODEL_NAME', 'mistral')

    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """
        Generates text based on the prompt using a local model, falling back to a cloud API.
        """
        try:
            return self._call_local_model(prompt, system_prompt, **kwargs)
        except Exception as e:
            logger.warning(f"Local model failed: {e}. Falling back to cloud API.")
            try:
                return self._call_cloud_api(prompt, system_prompt, **kwargs)
            except Exception as cloud_e:
                logger.error(f"Cloud API failed: {cloud_e}")
                raise

    def _call_local_model(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """
        Calls the local LLM API (e.g., Ollama).
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": kwargs
        }
        if system_prompt:
            payload["system"] = system_prompt

        response = requests.post(self.local_model_url, json=payload, timeout=10)
        response.raise_for_status()
        
        # Adjust based on actual API response format (Ollama uses 'response')
        return response.json().get('response', '')

    def _call_cloud_api(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """
        Calls a cloud LLM API (OpenAI compatible).
        """
        if not self.cloud_api_key:
            raise ValueError("Cloud API key not configured")
            
        headers = {
            "Authorization": f"Bearer {self.cloud_api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": "gpt-3.5-turbo", # Default fallback
            "messages": messages,
            **kwargs
        }
        
        response = requests.post(self.cloud_api_url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        # Adjust based on OpenAI API response format
        return response.json()['choices'][0]['message']['content']
