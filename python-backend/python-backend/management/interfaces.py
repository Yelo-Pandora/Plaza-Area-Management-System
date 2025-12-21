from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IValidationService(ABC):
    """
    数据验证服务接口
    
    负责验证数据的完整性、合法性和有效性
    """
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any], area_type: str) -> bool:
        """
        验证数据的完整性和合法性
        
        Args:
            data: 待验证的数据
            area_type: 区域类型
            
        Returns:
            bool: 验证是否通过
        """
        pass
    
    @abstractmethod
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        验证必填字段是否存在
        
        Args:
            data: 待验证的数据
            required_fields: 必填字段列表
            
        Returns:
            bool: 验证是否通过
        """
        pass
    
    @abstractmethod
    def validate_field_format(self, data: Dict[str, Any], field_name: str, field_type: type) -> bool:
        """
        验证字段格式是否正确
        
        Args:
            data: 待验证的数据
            field_name: 字段名称
            field_type: 字段类型
            
        Returns:
            bool: 验证是否通过
        """
        pass


class IDataProcessing(ABC):
    """
    数据处理服务接口
    
    负责数据的转换、清洗和处理
    """
    
    @abstractmethod
    def process_data(self, data: Dict[str, Any], area_type: str) -> Dict[str, Any]:
        """
        处理数据（转换、清洗等）
        
        Args:
            data: 待处理的数据
            area_type: 区域类型
            
        Returns:
            Dict[str, Any]: 处理后的数据
        """
        pass
    
    @abstractmethod
    def clean_data(self, data: Dict[str, Any], area_type: str) -> Dict[str, Any]:
        """
        清洗数据（移除无效字段、转换格式等）
        
        Args:
            data: 待清洗的数据
            area_type: 区域类型
            
        Returns:
            Dict[str, Any]: 清洗后的数据
        """
        pass
    
    @abstractmethod
    def transform_data(self, data: Dict[str, Any], area_type: str) -> Dict[str, Any]:
        """
        转换数据格式
        
        Args:
            data: 待转换的数据
            area_type: 区域类型
            
        Returns:
            Dict[str, Any]: 转换后的数据
        """
        pass
