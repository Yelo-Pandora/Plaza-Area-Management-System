from core.context import BaseContext
from .context import EditorContext
from django.db import transaction


class EditorService:
    """负责处理创建、更新及关联逻辑"""

    def create_element(self, area_type, data, map_id=None):
        """创建元素并自动关联地图"""
        # 1. 获取对应的 Model 和关联表 Model
        ModelClass, RelationModel, field_name = EditorContext.get_relation_model(area_type)
        if not ModelClass:
            raise ValueError("Invalid type")

        ctx = BaseContext(ModelClass)

        # 2. 事务原子性：创建对象 + 建立关联
        with transaction.atomic():
            # 创建实体
            instance = ctx.create(**data)

            # 如果提供了 map_id，建立关联
            if map_id:
                kwargs = {
                    field_name: instance,
                    'map_id': map_id
                }
                EditorContext.create_relation(RelationModel, **kwargs)

        return instance

    def update_element(self, area_type, instance_id, data):
        ModelClass, _, _ = EditorContext.get_relation_model(area_type)
        ctx = BaseContext(ModelClass)
        instance = ctx.get_by_id(instance_id)
        if not instance:
            return None
        return ctx.update(instance, **data)