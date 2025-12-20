import os
import time
import platform
import psutil
import json
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path

from ..models import ModelTier, HardwareBenchmark, ModelAvailability

logger = logging.getLogger(__name__)


class HardwareBenchmarker:
    """Benchmark system hardware capabilities"""
    
    @staticmethod
    def get_benchmark() -> HardwareBenchmark:
        """Get current hardware benchmark"""
        try:
            cpu_count = psutil.cpu_count(logical=False) or 1
            cpu_freq = psutil.cpu_freq()
            cpu_freq_ghz = cpu_freq.current / 1000 if cpu_freq else 2.0
            cpu_score = cpu_count * cpu_freq_ghz
            
            ram_info = psutil.virtual_memory()
            ram_gb = ram_info.total / (1024 ** 3)
            
            gpu_available = False
            gpu_memory_gb = 0.0
            
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_available = True
                    gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
            except ImportError:
                pass
            
            disk_speed_mbps = 100.0
            
            return HardwareBenchmark(
                cpu_score=cpu_score,
                ram_gb=ram_gb,
                gpu_available=gpu_available,
                gpu_memory_gb=gpu_memory_gb,
                disk_speed_mbps=disk_speed_mbps
            )
        except Exception as e:
            logger.warning(f"Hardware benchmark failed: {e}")
            return HardwareBenchmark(
                cpu_score=4.0,
                ram_gb=8.0,
                gpu_available=False,
                gpu_memory_gb=0.0,
                disk_speed_mbps=100.0
            )


class ModelManager:
    """Manage local and cloud LLM model selection with hardware-based fallback"""
    
    MODEL_CONFIGS = {
        "mistral-7b": {
            "tier": ModelTier.PREMIUM,
            "ram_requirement_gb": 16.0,
            "gpu_requirement_gb": 8.0,
            "cpu_score_min": 8.0,
            "model_path": "mistralai/Mistral-7B-Instruct-v0.2"
        },
        "phi-2": {
            "tier": ModelTier.STANDARD,
            "ram_requirement_gb": 8.0,
            "gpu_requirement_gb": 4.0,
            "cpu_score_min": 4.0,
            "model_path": "microsoft/phi-2"
        }
    }
    
    def __init__(self, cache_dir: str = ".model_cache", cloud_api_url: Optional[str] = None, cloud_api_key: Optional[str] = None):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cloud_api_url = cloud_api_url or os.getenv("CLOUD_LLM_API_URL")
        self.cloud_api_key = cloud_api_key or os.getenv("CLOUD_LLM_API_KEY")
        
        self.cache_file = self.cache_dir / "model_availability.json"
        self.cache_ttl = timedelta(hours=1)
        
        self.loaded_model = None
        self.loaded_model_name = None
        self.loaded_tokenizer = None
        
        self.hardware_benchmark = HardwareBenchmarker.get_benchmark()
        logger.info(f"Hardware benchmark: CPU={self.hardware_benchmark.cpu_score:.2f}, "
                   f"RAM={self.hardware_benchmark.ram_gb:.2f}GB, "
                   f"GPU={'Yes' if self.hardware_benchmark.gpu_available else 'No'}")
    
    def _load_cache(self) -> Optional[Dict[str, Any]]:
        """Load cached model availability"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    cache_time = datetime.fromisoformat(cache.get("timestamp", "2000-01-01"))
                    if datetime.now() - cache_time < self.cache_ttl:
                        return cache.get("models", {})
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
        return None
    
    def _save_cache(self, models: Dict[str, Any]):
        """Save model availability to cache"""
        try:
            cache = {
                "timestamp": datetime.now().isoformat(),
                "models": models
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def check_model_availability(self, model_name: str) -> ModelAvailability:
        """Check if a model can run on current hardware"""
        config = self.MODEL_CONFIGS.get(model_name)
        if not config:
            return ModelAvailability(
                model_name=model_name,
                tier=ModelTier.CLOUD,
                available=False,
                ram_requirement_gb=0.0,
                gpu_requirement_gb=0.0,
                last_checked=datetime.now()
            )
        
        ram_available = self.hardware_benchmark.ram_gb >= config["ram_requirement_gb"]
        cpu_available = self.hardware_benchmark.cpu_score >= config["cpu_score_min"]
        gpu_available = (
            self.hardware_benchmark.gpu_available and 
            self.hardware_benchmark.gpu_memory_gb >= config["gpu_requirement_gb"]
        ) if config["gpu_requirement_gb"] > 0 else True
        
        available = ram_available and cpu_available and (gpu_available or config["gpu_requirement_gb"] == 0)
        
        return ModelAvailability(
            model_name=model_name,
            tier=config["tier"],
            available=available,
            loaded=self.loaded_model_name == model_name,
            ram_requirement_gb=config["ram_requirement_gb"],
            gpu_requirement_gb=config["gpu_requirement_gb"],
            last_checked=datetime.now()
        )
    
    def select_model(self) -> Tuple[str, ModelTier]:
        """Select best available model based on hardware"""
        cached = self._load_cache()
        
        if cached:
            for model_name in ["mistral-7b", "phi-2"]:
                if cached.get(model_name, {}).get("available"):
                    return model_name, ModelTier(cached[model_name]["tier"])
        
        models_status = {}
        for model_name in ["mistral-7b", "phi-2"]:
            availability = self.check_model_availability(model_name)
            models_status[model_name] = {
                "available": availability.available,
                "tier": availability.tier.value
            }
            
            if availability.available:
                logger.info(f"Selected local model: {model_name} ({availability.tier.value})")
                self._save_cache(models_status)
                return model_name, availability.tier
        
        logger.info("No local models available, falling back to cloud API")
        self._save_cache(models_status)
        return "cloud", ModelTier.CLOUD
    
    def load_model(self, model_name: str) -> bool:
        """Load a local model (lazy loading)"""
        if self.loaded_model_name == model_name:
            return True
        
        if model_name == "cloud":
            return True
        
        config = self.MODEL_CONFIGS.get(model_name)
        if not config:
            logger.error(f"Unknown model: {model_name}")
            return False
        
        try:
            logger.info(f"Loading model {model_name}...")
            
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            model_path = config["model_path"]
            device = "cuda" if self.hardware_benchmark.gpu_available else "cpu"
            
            self.loaded_tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                cache_dir=str(self.cache_dir)
            )
            
            self.loaded_model = AutoModelForCausalLM.from_pretrained(
                model_path,
                cache_dir=str(self.cache_dir),
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                low_cpu_mem_usage=True
            )
            
            self.loaded_model.to(device)
            self.loaded_model_name = model_name
            
            logger.info(f"Model {model_name} loaded successfully on {device}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            self.loaded_model = None
            self.loaded_model_name = None
            self.loaded_tokenizer = None
            return False
    
    def generate_local(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> Optional[str]:
        """Generate text using loaded local model"""
        if not self.loaded_model or not self.loaded_tokenizer:
            logger.error("No model loaded")
            return None
        
        try:
            import torch
            
            inputs = self.loaded_tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
            device = "cuda" if self.hardware_benchmark.gpu_available else "cpu"
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.loaded_model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.loaded_tokenizer.eos_token_id
                )
            
            generated_text = self.loaded_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            if prompt in generated_text:
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Local generation failed: {e}")
            return None
    
    def generate_cloud(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> Optional[str]:
        """Generate text using cloud API"""
        if not self.cloud_api_url:
            logger.error("Cloud API URL not configured")
            return None
        
        try:
            import requests
            
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.cloud_api_key:
                headers["Authorization"] = f"Bearer {self.cloud_api_key}"
            
            payload = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(
                self.cloud_api_url,
                json=payload,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("text") or result.get("completion") or result.get("output")
            
        except Exception as e:
            logger.error(f"Cloud generation failed: {e}")
            return None
    
    def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> Tuple[Optional[str], str]:
        """Generate text using best available model"""
        model_name, tier = self.select_model()
        
        if tier == ModelTier.CLOUD:
            result = self.generate_cloud(prompt, max_tokens, temperature)
            return result, "cloud"
        
        if self.load_model(model_name):
            result = self.generate_local(prompt, max_tokens, temperature)
            if result:
                return result, model_name
        
        logger.warning(f"Local model {model_name} failed, falling back to cloud")
        result = self.generate_cloud(prompt, max_tokens, temperature)
        return result, "cloud-fallback"
    
    def unload_model(self):
        """Unload the current model to free memory"""
        if self.loaded_model:
            del self.loaded_model
            del self.loaded_tokenizer
            self.loaded_model = None
            self.loaded_tokenizer = None
            self.loaded_model_name = None
            
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass
            
            logger.info("Model unloaded")
