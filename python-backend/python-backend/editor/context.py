from core.models import Map, Storearea, Facility, Otherarea, Eventarea, StoreareaMap, FacilityMap, OtherareaMap, EventareaMap
from django.db.models import Q


class EditorContext:
    """负责编辑器的写入操作"""

    @staticmethod
    def create_relation(model_class, **kwargs):
        """创建中间表关联"""
        model_class.objects.get_or_create(**kwargs)

    @staticmethod
    def get_relation_model(type_str):
        if type_str == 'store': return Storearea, StoreareaMap, 'storearea'
        if type_str == 'facility': return Facility, FacilityMap, 'facility'
        if type_str == 'other': return Otherarea, OtherareaMap, 'otherarea'
        if type_str == 'event': return Eventarea, EventareaMap, 'eventarea'
        return None, None, None