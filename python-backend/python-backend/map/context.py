from core.models import Map, Storearea, Facility, Otherarea, Eventarea
from django.db.models import Q
from core.context import BaseContext


class MapContext(BaseContext):
    def __init__(self):
        super().__init__(Map)

    def get_map_with_building(self, map_id):
        """获取地图并预加载建筑信息"""
        try:
            return self.model.objects.select_related('building').get(pk=map_id)
        except self.model.DoesNotExist:
            return None

    @staticmethod
    def get_map_elements(map_obj):
        """一次性获取地图关联的所有元素 ID"""
        # 注意：这里只负责取数据，不负责格式化
        store_ids = map_obj.storeareamap_set.values_list('storearea_id', flat=True)
        facility_ids = map_obj.facilitymap_set.values_list('facility_id', flat=True)
        other_ids = map_obj.otherareamap_set.values_list('otherarea_id', flat=True)
        event_ids = map_obj.eventareamap_set.values_list('eventarea_id', flat=True)
        return store_ids, facility_ids, other_ids, event_ids

    def list_all_with_building(self):
        """获取所有地图列表，并预加载建筑信息"""
        return self.model.objects.select_related('building').all()

    def check_exists(self, building_id, floor_number):
        """检查特定楼层是否存在"""
        return self.model.objects.filter(building_id=building_id, floor_number=floor_number).exists()

    def create_map_record(self, building_id, floor_number, geometry):
        """创建地图记录"""
        return self.create(
            building_id=building_id,
            floor_number=floor_number,
            detail=geometry
        )

class ElementContext:
    """负责处理具体的商铺、设施等元素"""

    @staticmethod
    def get_stores_by_ids(ids):
        return Storearea.objects.filter(id__in=ids)

    @staticmethod
    def get_facilities_by_ids(ids):
        return Facility.objects.filter(id__in=ids)

    @staticmethod
    def get_others_by_ids(ids):
        return Otherarea.objects.filter(id__in=ids)

    @staticmethod
    def get_events_by_ids(ids):
        return Eventarea.objects.filter(id__in=ids)

    @staticmethod
    def search_globally(keyword):
        stores = Storearea.objects.filter(store_name__icontains=keyword)
        others = Otherarea.objects.filter(description__icontains=keyword, is_public=True)
        return stores, others