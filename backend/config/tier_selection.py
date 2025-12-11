from typing import Dict, Any, Literal

TierType = Literal['Premium', 'Standard', 'Minimum']


class TierSelector:
    def __init__(self, hardware_info: Dict[str, Any]):
        self.hardware_info = hardware_info
        self.current_tier: TierType = 'Minimum'
    
    def select_tier(self) -> TierType:
        ram_gb = self.hardware_info.get('ram_gb', 0)
        has_gpu = self.hardware_info.get('has_gpu', False)
        
        if ram_gb >= 16 and has_gpu:
            self.current_tier = 'Premium'
        elif ram_gb >= 8:
            self.current_tier = 'Standard'
        else:
            self.current_tier = 'Minimum'
        
        return self.current_tier
    
    def get_current_tier(self) -> TierType:
        return self.current_tier
    
    def get_tier_config(self) -> Dict[str, Any]:
        configs = {
            'Premium': {
                'max_concurrent_tasks': 4,
                'embedding_model': 'all-MiniLM-L6-v2',
                'use_gpu': True,
                'batch_size': 64,
                'cache_size_mb': 1024
            },
            'Standard': {
                'max_concurrent_tasks': 2,
                'embedding_model': 'all-MiniLM-L6-v2',
                'use_gpu': False,
                'batch_size': 32,
                'cache_size_mb': 512
            },
            'Minimum': {
                'max_concurrent_tasks': 1,
                'embedding_model': 'all-MiniLM-L6-v2',
                'use_gpu': False,
                'batch_size': 16,
                'cache_size_mb': 256
            }
        }
        
        return configs[self.current_tier]
    
    def can_upgrade_tier(self) -> bool:
        return self.current_tier != 'Premium'
    
    def can_downgrade_tier(self) -> bool:
        return self.current_tier != 'Minimum'
