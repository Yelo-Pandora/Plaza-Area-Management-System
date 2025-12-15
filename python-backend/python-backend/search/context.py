from django.apps import apps
from django.db.models import Q


class BaseSearchContext:
    """基础搜索上下文类"""

    def __init__(self, model_name):
        self.model_name = model_name
        self.model = apps.get_model('core', model_name)


class StoreareaContext(BaseSearchContext):
    """店铺区域上下文"""

    def __init__(self):
        super().__init__('Storearea')

    def get_by_id(self, storearea_id):
        """根据ID获取店铺区域"""
        try:
            return self.model.objects.get(id=storearea_id)
        except self.model.DoesNotExist:
            return None

    def search_by_name(self, name):
        """根据名称搜索店铺区域"""
        return self.model.objects.filter(
            store_name__icontains=name,
            is_active=True
        )

    def filter_by_type(self, type_id=None, is_active=True):
        """根据类型筛选店铺区域"""
        queryset = self.model.objects.all()
        if is_active:
            queryset = queryset.filter(is_active=True)
        if type_id is not None:
            queryset = queryset.filter(type=type_id)
        return queryset

    def get_storearea_map_relations(self, storearea_id):
        """获取店铺区域的地图关联"""
        StoreareaMap = apps.get_model('core', 'StoreareaMap')
        return StoreareaMap.objects.filter(storearea_id=storearea_id)


class EventContext(BaseSearchContext):
    """活动上下文"""

    def __init__(self):
        super().__init__('Event')

    def get_by_id(self, event_id):
        """根据ID获取活动"""
        try:
            return self.model.objects.get(id=event_id)
        except self.model.DoesNotExist:
            return None

    def search_by_name(self, name):
        """根据名称搜索活动"""
        return self.model.objects.filter(
            event_name__icontains=name,
            is_active=True
        )

    def filter_active_events(self):
        """获取所有活跃活动"""
        return self.model.objects.filter(is_active=True)

    def get_event_storearea_relations(self, event_id):
        """获取活动的店铺区域关联"""
        EventStorearea = apps.get_model('core', 'EventStorearea')
        return EventStorearea.objects.filter(event_id=event_id)

    def get_event_eventarea_relations(self, event_id):
        """获取活动的活动区域关联"""
        EventEventarea = apps.get_model('core', 'EventEventarea')
        return EventEventarea.objects.filter(event_id=event_id)


class EventareaContext(BaseSearchContext):
    """活动区域上下文"""

    def __init__(self):
        super().__init__('Eventarea')

    def get_by_id(self, eventarea_id):
        """根据ID获取活动区域"""
        try:
            return self.model.objects.get(id=eventarea_id)
        except self.model.DoesNotExist:
            return None

    def filter_by_type(self, type_id=None, is_active=True):
        """根据类型筛选活动区域"""
        queryset = self.model.objects.all()
        if is_active:
            queryset = queryset.filter(is_active=True)
        if type_id is not None:
            queryset = queryset.filter(type=type_id)
        return queryset

    def get_eventarea_map_relations(self, eventarea_id):
        """获取活动区域的地图关联"""
        EventareaMap = apps.get_model('core', 'EventareaMap')
        return EventareaMap.objects.filter(eventarea_id=eventarea_id)

    def get_eventarea_map_relations_by_map(self, map_id):
        """根据地图ID获取活动区域关联"""
        EventareaMap = apps.get_model('core', 'EventareaMap')
        return EventareaMap.objects.filter(map_id=map_id)


class FacilityContext(BaseSearchContext):
    """设施上下文"""

    def __init__(self):
        super().__init__('Facility')

    def get_by_id(self, facility_id):
        """根据ID获取设施"""
        try:
            return self.model.objects.get(id=facility_id)
        except self.model.DoesNotExist:
            return None

    def filter_by_type(self, type_id=None, is_active=True):
        """根据类型筛选设施"""
        queryset = self.model.objects.all()
        if is_active:
            queryset = queryset.filter(is_active=True)
        if type_id is not None:
            queryset = queryset.filter(type=type_id)
        return queryset

    def get_facility_map_relations(self, facility_id):
        """获取设施的地图关联"""
        FacilityMap = apps.get_model('core', 'FacilityMap')
        return FacilityMap.objects.filter(facility_id=facility_id)

    def get_facility_map_relations_by_map(self, map_id):
        """根据地图ID获取设施关联"""
        FacilityMap = apps.get_model('core', 'FacilityMap')
        return FacilityMap.objects.filter(map_id=map_id)


class OtherareaContext(BaseSearchContext):
    """其他区域上下文"""

    def __init__(self):
        super().__init__('Otherarea')

    def get_by_id(self, otherarea_id):
        """根据ID获取其他区域"""
        try:
            return self.model.objects.get(id=otherarea_id)
        except self.model.DoesNotExist:
            return None

    def filter_by_type(self, type_id=None, is_active=True):
        """根据类型筛选其他区域"""
        queryset = self.model.objects.all()
        if is_active:
            queryset = queryset.filter(is_active=True)
        if type_id is not None:
            queryset = queryset.filter(type=type_id)
        return queryset

    def get_otherarea_map_relations(self, otherarea_id):
        """获取其他区域的地图关联"""
        OtherareaMap = apps.get_model('core', 'OtherareaMap')
        return OtherareaMap.objects.filter(otherarea_id=otherarea_id)

    def get_otherarea_map_relations_by_map(self, map_id):
        """根据地图ID获取其他区域关联"""
        OtherareaMap = apps.get_model('core', 'OtherareaMap')
        return OtherareaMap.objects.filter(map_id=map_id)


class SearchElementContext:
    """搜索元素上下文，用于处理关联关系"""

    @staticmethod
    def get_storearea_ids_by_map_and_type(map_id, type_id=None):
        """根据地图和类型获取店铺区域ID"""
        StoreareaMap = apps.get_model('core', 'StoreareaMap')
        Storearea = apps.get_model('core', 'Storearea')

        # 获取该地图的所有storearea关联
        storearea_maps = StoreareaMap.objects.filter(map_id=map_id)
        storearea_ids = [sm.storearea_id for sm in storearea_maps]

        # 如果提供了类型参数，则进一步过滤
        if type_id is not None:
            storeareas = Storearea.objects.filter(
                id__in=storearea_ids,
                type=type_id,
                is_active=True
            )
            storearea_ids = [storearea.id for storearea in storeareas]

        return storearea_ids

    @staticmethod
    def get_eventarea_ids_by_map_and_type(map_id, type_id=None):
        """根据地图和类型获取活动区域ID"""
        EventareaMap = apps.get_model('core', 'EventareaMap')
        Eventarea = apps.get_model('core', 'Eventarea')

        eventarea_maps = EventareaMap.objects.filter(map_id=map_id)
        eventarea_ids = [em.eventarea_id for em in eventarea_maps]

        if type_id is not None:
            eventareas = Eventarea.objects.filter(
                id__in=eventarea_ids,
                type=type_id,
                is_active=True
            )
            eventarea_ids = [eventarea.id for eventarea in eventareas]

        return eventarea_ids

    @staticmethod
    def get_facility_ids_by_map_and_type(map_id, type_id=None):
        """根据地图和类型获取设施ID"""
        FacilityMap = apps.get_model('core', 'FacilityMap')
        Facility = apps.get_model('core', 'Facility')

        facility_maps = FacilityMap.objects.filter(map_id=map_id)
        facility_ids = [fm.facility_id for fm in facility_maps]

        if type_id is not None:
            facilities = Facility.objects.filter(
                id__in=facility_ids,
                type=type_id,
                is_active=True
            )
            facility_ids = [facility.id for facility in facilities]

        return facility_ids

    @staticmethod
    def get_otherarea_ids_by_map_and_type(map_id, type_id=None):
        """根据地图和类型获取其他区域ID"""
        OtherareaMap = apps.get_model('core', 'OtherareaMap')
        Otherarea = apps.get_model('core', 'Otherarea')

        otherarea_maps = OtherareaMap.objects.filter(map_id=map_id)
        otherarea_ids = [om.otherarea_id for om in otherarea_maps]

        if type_id is not None:
            otherareas = Otherarea.objects.filter(
                id__in=otherarea_ids,
                type=type_id,
                is_active=True
            )
            otherarea_ids = [otherarea.id for otherarea in otherareas]

        return otherarea_ids