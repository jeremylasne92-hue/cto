import psutil
import platform
from typing import Dict, Any

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False


class HardwareDetector:
    def __init__(self):
        self.cache = None
    
    def detect(self) -> Dict[str, Any]:
        if self.cache:
            return self.cache
        
        ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        
        has_gpu = False
        gpu_info = []
        
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    has_gpu = True
                    for gpu in gpus:
                        gpu_info.append({
                            'name': gpu.name,
                            'memory_mb': gpu.memoryTotal,
                            'driver': gpu.driver
                        })
            except Exception:
                pass
        
        cpu_count = psutil.cpu_count(logical=False) or 1
        cpu_count_logical = psutil.cpu_count(logical=True) or 1
        
        self.cache = {
            'ram_gb': ram_gb,
            'has_gpu': has_gpu,
            'gpu_info': gpu_info,
            'cpu_count': cpu_count,
            'cpu_count_logical': cpu_count_logical,
            'platform': platform.system(),
            'platform_version': platform.version()
        }
        
        return self.cache
    
    def benchmark_ram_speed(self) -> float:
        import time
        import numpy as np
        
        size = 100_000_000
        start = time.time()
        arr = np.random.rand(size)
        result = np.sum(arr)
        end = time.time()
        
        return end - start
    
    def clear_cache(self):
        self.cache = None
