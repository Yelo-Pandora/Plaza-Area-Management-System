from rest_framework import status
from django.apps import apps
from .context import (
    StoreareaContext, EventContext, EventareaContext,
    FacilityContext, OtherareaContext, SearchElementContext
)


class SearchService:
    """搜索服务"""

    def __init__(self):
        self.storearea_ctx = StoreareaContext()
        self.event_ctx = EventContext()
        self.eventarea_ctx = EventareaContext()
        self.facility_ctx = FacilityContext()
        self.otherarea_ctx = OtherareaContext()
        self.element_ctx = SearchElementContext()

    # ========== 店铺搜索功能 ==========

    def get_storearea_by_id(self, storearea_id):
        """获取ID为<>的商铺区域的所有信息"""
        storearea = self.storearea_ctx.get_by_id(storearea_id)
        if not storearea:
            return None, {'error': 'Storearea not found'}, status.HTTP_404_NOT_FOUND
        return storearea, None, None

    def search_storearea_by_name(self, name):
        """按名称寻找店铺区域"""
        if not name:
            return None, {'error': 'Name parameter is required'}, status.HTTP_400_BAD_REQUEST
        storeareas = self.storearea_ctx.search_by_name(name)
        return storeareas, None, None

    def list_storearea_by_type(self, type_param):
        """返回指定类型店铺区域列表"""
        if type_param:
            try:
                type_id = int(type_param)
                storeareas = self.storearea_ctx.filter_by_type(type_id=type_id)
                return storeareas, {'type': type_id}, None
            except ValueError:
                return None, {'error': 'Invalid type parameter'}, status.HTTP_400_BAD_REQUEST
        else:
            storeareas = self.storearea_ctx.filter_by_type()
            return storeareas, None, None

    def get_storearea_events(self, storearea_id):
        """返回指定店铺区域的所有活动ID列表"""
        storearea = self.storearea_ctx.get_by_id(storearea_id)
        if not storearea or not storearea.is_active:
            return None, {'error': 'Storearea not found'}, status.HTTP_404_NOT_FOUND

        EventStorearea = apps.get_model('core', 'EventStorearea')
        event_relations = EventStorearea.objects.filter(storearea_id=storearea_id)
        event_ids = [relation.event_id for relation in event_relations]

        return {'storearea_id': storearea_id, 'event_ids': event_ids}, None, None

    def get_storearea_map_ids(self, storearea_id):
        """获取storearea_id为<>的活动区域所属的map_id"""
        storearea_maps = self.storearea_ctx.get_storearea_map_relations(storearea_id)
        map_ids = [storearea_map.map_id for storearea_map in storearea_maps]
        return {'storearea_id': storearea_id, 'map_ids': map_ids}, None, None

    def get_storearea_ids_by_map_and_type(self, map_id_str, type_param):
        """获取map_id为<> 且type为<>的所有storearea的id"""
        if not map_id_str:
            return None, {'error': 'map_id parameter is required'}, status.HTTP_400_BAD_REQUEST

        try:
            map_id = int(map_id_str)
            type_id = int(type_param) if type_param else None

            storearea_ids = self.element_ctx.get_storearea_ids_by_map_and_type(map_id, type_id)

            result = {
                'map_id': map_id,
                'type': type_id if type_param else None,
                'storearea_ids': storearea_ids
            }
            return result, None, None
        except ValueError:
            return None, {'error': 'Invalid parameter'}, status.HTTP_400_BAD_REQUEST

    def get_all_storearea_ids_by_map(self, map_id_str):
        """获取map_id为<>的地图对应的所有storearea_id"""
        if not map_id_str:
            return None, {'error': 'map_id parameter is required'}, status.HTTP_400_BAD_REQUEST

        try:
            map_id = int(map_id_str)
            storearea_ids = self.element_ctx.get_storearea_ids_by_map_and_type(map_id)

            result = {
                'map_id': map_id,
                'storearea_ids': storearea_ids
            }
            return result, None, None
        except ValueError:
            return None, {'error': 'Invalid map_id parameter'}, status.HTTP_400_BAD_REQUEST

    # ========== 活动搜索功能 ==========

    def get_event_by_id(self, event_id):
        """按ID寻找活动"""
        event = self.event_ctx.get_by_id(event_id)
        if not event:
            return None, {'error': 'Event not found'}, status.HTTP_404_NOT_FOUND
        return event, None, None

    def search_event_by_name(self, name):
        """按名称寻找活动"""
        if not name:
            return None, {'error': 'Name parameter is required'}, status.HTTP_400_BAD_REQUEST
        events = self.event_ctx.search_by_name(name)
        return events, None, None

    def list_event_by_type(self, type_param):
        """返回指定类型活动列表"""
        events = self.event_ctx.filter_active_events()

        if type_param:
            try:
                type_id = int(type_param)
                EventEventarea = apps.get_model('core', 'EventEventarea')
                event_ids = EventEventarea.objects.filter(
                    eventarea__type=type_id
                ).values_list('event_id', flat=True).distinct()

                events = events.filter(id__in=event_ids)
                return events, {'type': type_id}, None
            except ValueError:
                return None, {'error': 'Invalid type parameter'}, status.HTTP_400_BAD_REQUEST
        else:
            return events, None, None

    def get_event_areas(self, event_id):
        """返回参加该活动的区域ID列表"""
        event = self.event_ctx.get_by_id(event_id)
        if not event:
            return None, {'error': 'Event not found'}, status.HTTP_404_NOT_FOUND

        storearea_relations = self.event_ctx.get_event_storearea_relations(event_id)
        storearea_ids = [relation.storearea_id for relation in storearea_relations]

        eventarea_relations = self.event_ctx.get_event_eventarea_relations(event_id)
        eventarea_ids = [relation.eventarea_id for relation in eventarea_relations]

        result = {
            'event_id': event_id,
            'storearea_ids': storearea_ids,
            'eventarea_ids': eventarea_ids,
            'all_area_ids': storearea_ids + eventarea_ids
        }
        return result, None, None

    # ========== 活动区域功能 ==========

    def get_eventarea_by_id(self, eventarea_id):
        """获取id为<>的活动区域的所有信息"""
        eventarea = self.eventarea_ctx.get_by_id(eventarea_id)
        if not eventarea:
            return None, {'error': 'Eventarea not found'}, status.HTTP_404_NOT_FOUND
        return eventarea, None, None

    def get_eventarea_ids_by_map_and_type(self, map_id_str, type_param):
        """获取map_id为<> 且 type为<>的所有eventarea的id"""
        if not map_id_str:
            return None, {'error': 'map_id parameter is required'}, status.HTTP_400_BAD_REQUEST

        try:
            map_id = int(map_id_str)
            type_id = int(type_param) if type_param else None

            eventarea_ids = self.element_ctx.get_eventarea_ids_by_map_and_type(map_id, type_id)

            result = {
                'map_id': map_id,
                'type': type_id if type_param else None,
                'eventarea_ids': eventarea_ids
            }
            return result, None, None
        except ValueError:
            return None, {'error': 'Invalid parameter'}, status.HTTP_400_BAD_REQUEST

    def get_eventarea_map_ids(self, eventarea_id):
        """获取eventarea_id为<>的活动区域所属的map_id"""
        eventarea_maps = self.eventarea_ctx.get_eventarea_map_relations(eventarea_id)
        map_ids = [eventarea_map.map_id for eventarea_map in eventarea_maps]
        return {'eventarea_id': eventarea_id, 'map_ids': map_ids}, None, None

    def get_all_eventarea_ids_by_map(self, map_id_str):
        """获取map_id为<>的地图对应的所有eventarea_id"""
        if not map_id_str:
            return None, {'error': 'map_id parameter is required'}, status.HTTP_400_BAD_REQUEST

        try:
            map_id = int(map_id_str)
            eventarea_ids = self.element_ctx.get_eventarea_ids_by_map_and_type(map_id)

            result = {
                'map_id': map_id,
                'eventarea_ids': eventarea_ids
            }
            return result, None, None
        except ValueError:
            return None, {'error': 'Invalid map_id parameter'}, status.HTTP_400_BAD_REQUEST

    # ========== 设施功能 ==========

    def get_facility_by_id(self, facility_id):
        """获取id为<>的设施的所有信息"""
        facility = self.facility_ctx.get_by_id(facility_id)
        if not facility:
            return None, {'error': 'Facility not found'}, status.HTTP_404_NOT_FOUND
        return facility, None, None

    def get_facility_ids_by_map_and_type(self, map_id_str, type_param):
        """获取map_id为<> 且type为<>的所有设施id"""
        if not map_id_str:
            return None, {'error': 'map_id parameter is required'}, status.HTTP_400_BAD_REQUEST

        try:
            map_id = int(map_id_str)
            type_id = int(type_param) if type_param else None

            facility_ids = self.element_ctx.get_facility_ids_by_map_and_type(map_id, type_id)

            result = {
                'map_id': map_id,
                'type': type_id if type_param else None,
                'facility_ids': facility_ids
            }
            return result, None, None
        except ValueError:
            return None, {'error': 'Invalid parameter'}, status.HTTP_400_BAD_REQUEST

    def get_facility_map_ids(self, facility_id):
        """获取facility_id为<>的活动区域所属的map_id"""
        facility_maps = self.facility_ctx.get_facility_map_relations(facility_id)
        map_ids = [facility_map.map_id for facility_map in facility_maps]
        return {'facility_id': facility_id, 'map_ids': map_ids}, None, None

    def get_all_facility_ids_by_map(self, map_id_str):
        """获取map_id为<>的地图对应的所有facility_id"""
        if not map_id_str:
            return None, {'error': 'map_id parameter is required'}, status.HTTP_400_BAD_REQUEST

        try:
            map_id = int(map_id_str)
            facility_ids = self.element_ctx.get_facility_ids_by_map_and_type(map_id)

            result = {
                'map_id': map_id,
                'facility_ids': facility_ids
            }
            return result, None, None
        except ValueError:
            return None, {'error': 'Invalid map_id parameter'}, status.HTTP_400_BAD_REQUEST

    # ========== 其他区域功能 ==========

    def get_otherarea_by_id(self, otherarea_id):
        """获取id为<>的其他区域的所有信息"""
        otherarea = self.otherarea_ctx.get_by_id(otherarea_id)
        if not otherarea:
            return None, {'error': 'Otherarea not found'}, status.HTTP_404_NOT_FOUND
        return otherarea, None, None

    def get_otherarea_ids_by_map_and_type(self, map_id_str, type_param):
        """获取map_id为<> 且type为<>的所有otherarea的id"""
        if not map_id_str:
            return None, {'error': 'map_id parameter is required'}, status.HTTP_400_BAD_REQUEST

        try:
            map_id = int(map_id_str)
            type_id = int(type_param) if type_param else None

            otherarea_ids = self.element_ctx.get_otherarea_ids_by_map_and_type(map_id, type_id)

            result = {
                'map_id': map_id,
                'type': type_id if type_param else None,
                'otherarea_ids': otherarea_ids
            }
            return result, None, None
        except ValueError:
            return None, {'error': 'Invalid parameter'}, status.HTTP_400_BAD_REQUEST

    def get_otherarea_map_ids(self, otherarea_id):
        """获取otherarea_id为<>的活动区域所属的map_id"""
        otherarea_maps = self.otherarea_ctx.get_otherarea_map_relations(otherarea_id)
        map_ids = [otherarea_map.map_id for otherarea_map in otherarea_maps]
        return {'otherarea_id': otherarea_id, 'map_ids': map_ids}, None, None

    def get_all_otherarea_ids_by_map(self, map_id_str):
        """获取map_id为<>的地图对应的所有otherarea_id"""
        if not map_id_str:
            return None, {'error': 'map_id parameter is required'}, status.HTTP_400_BAD_REQUEST

        try:
            map_id = int(map_id_str)
            otherarea_ids = self.element_ctx.get_otherarea_ids_by_map_and_type(map_id)

            result = {
                'map_id': map_id,
                'otherarea_ids': otherarea_ids
            }
            return result, None, None
        except ValueError:
            return None, {'error': 'Invalid map_id parameter'}, status.HTTP_400_BAD_REQUEST