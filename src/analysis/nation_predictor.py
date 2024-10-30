from typing import Dict, List, Tuple
import numpy as np
from collections import Counter

class NationPredictor:
    """
    基于关系网络的开发者所属国家/地区推断
    """
    
    def __init__(self):
        self.location_mapping = self._load_location_mapping()
    
    def predict_nation(self, 
                      developer_location: str,
                      network_locations: List[str]) -> Tuple[str, float]:
        """
        预测开发者所属国家/地区
        返回：(预测的国家/地区, 置信度)
        """
        # 如果开发者已明确标注位置
        if developer_location:
            mapped_nation = self._map_location_to_nation(developer_location)
            if mapped_nation:
                return mapped_nation, 1.0
        
        # 基于关系网络推断
        return self._predict_from_network(network_locations)
    
    def _predict_from_network(self, network_locations: List[str]) -> Tuple[str, float]:
        """
        基于关系网络位置信息进行预测
        """
        # 过滤并映射位置信息
        mapped_nations = [
            self._map_location_to_nation(loc) 
            for loc in network_locations 
            if loc and self._map_location_to_nation(loc)
        ]
        
        if not mapped_nations:
            return "Unknown", 0.0
            
        # 统计出现频率最高的国家/地区
        nation_counts = Counter(mapped_nations)
        total_valid = len(mapped_nations)
        
        most_common = nation_counts.most_common(1)[0]
        nation = most_common[0]
        confidence = most_common[1] / total_valid
        
        return nation, confidence
    
    def _map_location_to_nation(self, location: str) -> str:
        """
        将位置信息映射到标准国家/地区名称
        """
        if not location:
            return None
            
        location = location.lower().strip()
        
        # 使用预定义的映射关系
        for nation, keywords in self.location_mapping.items():
            if any(keyword in location for keyword in keywords):
                return nation
                
        return None
    
    def _load_location_mapping(self) -> Dict[str, List[str]]:
        """
        加载位置信息映射表
        """
        return {
            "China": ["china", "cn", "beijing", "shanghai", "guangzhou", "shenzhen"],
            "United States": ["usa", "us", "united states", "california", "new york"],
            "India": ["india", "bangalore", "mumbai", "delhi"],
            "United Kingdom": ["uk", "united kingdom", "london", "manchester"],
            # 可以继续添加更多国家/地区的映射
        } 