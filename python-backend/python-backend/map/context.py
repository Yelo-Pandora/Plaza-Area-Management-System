from django.db import models
from django.db.models import Q
from core.models import Map
# Create your models here.
class MapContext:
    @staticmethod
    def list_all_maps():
        """
        获取所有 Map 对象。
        """
        return Map.objects.select_related('building').all()

    @staticmethod
    def get_map_by_id(map_id):
        """
        (可选) 根据 ID 获取单个 Map
        """
        try:
            return Map.objects.select_related('building').get(pk=map_id)
        except Map.DoesNotExist:
            return None