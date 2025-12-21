from abc import ABC, abstractmethod
from typing import Any, Optional


class IShapeEditor(ABC):
    """形状编辑器接口"""
    
    @abstractmethod
    def create_element(self, area_type: str, data: dict, map_id: Optional[int] = None) -> Any:
        """创建元素
        
        Args:
            area_type: 区域类型
            data: 元素数据
            map_id: 地图ID（可选）
            
        Returns:
            创建的元素实例
        """
        pass
    
    @abstractmethod
    def update_element(self, area_type: str, instance_id: int, data: dict) -> Any:
        """更新元素
        
        Args:
            area_type: 区域类型
            instance_id: 元素ID
            data: 更新的数据
            
        Returns:
            更新后的元素实例
        """
        pass
    
    @abstractmethod
    def delete_element(self, area_type: str, instance_id: int) -> Any:
        """删除元素
        
        Args:
            area_type: 区域类型
            instance_id: 元素ID
            
        Returns:
            删除结果
        """
        pass


class IShapeValidator(ABC):
    """形状验证器接口"""
    
    @abstractmethod
    def validate_shape(self, shape: Any) -> bool:
        """验证形状有效性
        
        Args:
            shape: 形状数据
            
        Returns:
            形状是否有效
        """
        pass
    
    @abstractmethod
    def validate_placement(self, shape: Any, map_id: int) -> bool:
        """验证形状在地图上的放置位置
        
        Args:
            shape: 形状数据
            map_id: 地图ID
            
        Returns:
            放置位置是否有效
        """
        pass