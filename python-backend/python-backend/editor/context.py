from django.contrib.gis.geos import GEOSGeometry
from core.models import (
    Event,
    Storearea,
    StoreareaMap,
    EventStorearea,
    EventEventarea,
    Eventarea,
    EventareaMap,
    Otherarea,
    OtherareaMap,
    Facility,
    FacilityMap
)


class StoreareaContext:
    """
    店铺区域（Storearea）的数据访问层
    负责与数据库交互，仅提供shape属性相关的操作
    """

    @staticmethod
    def get_all():
        """获取所有店铺区域"""
        return Storearea.objects.all()

    @staticmethod
    def get_by_id(storearea_id):
        """根据ID获取店铺区域"""
        return Storearea.objects.filter(id=storearea_id).first()

    @staticmethod
    def create(shape, map_id=None):
        """创建新的店铺区域，并可选绑定到指定地图"""
        # 将shape字符串转换为GEOSGeometry对象，支持WKT和GeoJSON格式
        try:
            # 直接解析，并明确指定SRID=2385
            # 这样无论是WKT还是GeoJSON格式，都会使用正确的SRID
            shape_geom = GEOSGeometry(shape, srid=2385)
        except Exception as e:
            raise ValueError(f"Invalid spatial data. Failed to parse geometry: {str(e)}")
        
        # 确保SRID为2385（双重保险）
        if shape_geom.srid != 2385:
            shape_geom.srid = 2385
        
        storearea = Storearea.objects.create(shape=shape_geom)
        # 绑定到地图
        if map_id is not None:
            StoreareaMap.objects.create(storearea=storearea, map_id=map_id)
        return storearea

    @staticmethod
    def update_shape(storearea_id, shape):
        """更新店铺区域的形状"""
        # 将shape字符串转换为GEOSGeometry对象，支持WKT和GeoJSON格式
        try:
            # 直接解析，并明确指定SRID=2385
            shape_geom = GEOSGeometry(shape, srid=2385)
        except Exception as e:
            raise ValueError(f"Invalid spatial data. Failed to parse geometry: {str(e)}")
        
        # 确保SRID为2385（双重保险）
        if shape_geom.srid != 2385:
            shape_geom.srid = 2385
        
        Storearea.objects.filter(id=storearea_id).update(shape=shape_geom)
        return StoreareaContext.get_by_id(storearea_id)

    @staticmethod
    def delete(storearea_id):
        """删除店铺区域"""
        Storearea.objects.filter(id=storearea_id).delete()

    @staticmethod
    def delete_many(storearea_ids):
        """批量删除店铺区域"""
        if storearea_ids:
            Storearea.objects.filter(id__in=storearea_ids).delete()

    @staticmethod
    def get_events_by_storearea(storearea_id):
        """获取店铺关联的所有活动ID"""
        event_relations = EventStorearea.objects.filter(storearea_id=storearea_id)
        return [relation.event_id for relation in event_relations]


class EventContext:
    """
    活动（Event）的数据访问层
    负责与数据库交互，仅提供shape属性相关的操作
    """

    @staticmethod
    def get_all():
        """获取所有活动"""
        return Event.objects.all()

    @staticmethod
    def get_by_id(event_id):
        """根据ID获取活动"""
        return Event.objects.filter(id=event_id).first()



    @staticmethod
    def get_storeareas_by_event(event_id):
        """获取活动关联的所有店铺区域ID"""
        storearea_relations = EventStorearea.objects.filter(event_id=event_id)
        return [relation.storearea_id for relation in storearea_relations]

    @staticmethod
    def get_eventareas_by_event(event_id):
        """获取活动关联的所有活动区域ID"""
        eventarea_relations = EventEventarea.objects.filter(event_id=event_id)
        return [relation.eventarea_id for relation in eventarea_relations]

    @staticmethod
    def add_storearea_relation(event_id, storearea_id):
        """添加活动与店铺区域的关联关系"""
        return EventStorearea.objects.get_or_create(event_id=event_id, storearea_id=storearea_id)

    @staticmethod
    def remove_storearea_relation(event_id, storearea_id):
        """移除活动与店铺区域的关联关系"""
        return EventStorearea.objects.filter(event_id=event_id, storearea_id=storearea_id).delete()

    @staticmethod
    def add_eventarea_relation(event_id, eventarea_id):
        """添加活动与活动区域的关联关系"""
        return EventEventarea.objects.get_or_create(event_id=event_id, eventarea_id=eventarea_id)

    @staticmethod
    def remove_eventarea_relation(event_id, eventarea_id):
        """移除活动与活动区域的关联关系"""
        return EventEventarea.objects.filter(event_id=event_id, eventarea_id=eventarea_id).delete()


class EventareaContext:
    """
    活动区域（Eventarea）的数据访问层
    负责与数据库交互，提供基本的CRUD操作
    """

    @staticmethod
    def get_all():
        """获取所有活动区域"""
        return Eventarea.objects.all()

    @staticmethod
    def get_by_id(eventarea_id):
        """根据ID获取活动区域"""
        return Eventarea.objects.filter(id=eventarea_id).first()

    @staticmethod
    def create(shape, map_id=None):
        """创建新的活动区域，并可选绑定到指定地图"""
        # 将shape字符串转换为GEOSGeometry对象，支持WKT和GeoJSON格式
        try:
            # 直接解析，并明确指定SRID=2385
            shape_geom = GEOSGeometry(shape, srid=2385)
        except Exception as e:
            raise ValueError(f"Invalid spatial data. Failed to parse geometry: {str(e)}")
        
        # 确保SRID为2385（双重保险）
        if shape_geom.srid != 2385:
            shape_geom.srid = 2385
        
        eventarea = Eventarea.objects.create(shape=shape_geom)
        if map_id is not None:
            EventareaMap.objects.create(eventarea=eventarea, map_id=map_id)
        return eventarea

    @staticmethod
    def update_shape(eventarea_id, shape):
        """更新活动区域的形状"""
        # 将shape字符串转换为GEOSGeometry对象，支持WKT和GeoJSON格式
        try:
            # 直接解析，并明确指定SRID=2385
            shape_geom = GEOSGeometry(shape, srid=2385)
        except Exception as e:
            raise ValueError(f"Invalid spatial data. Failed to parse geometry: {str(e)}")
        
        # 确保SRID为2385（双重保险）
        if shape_geom.srid != 2385:
            shape_geom.srid = 2385
        
        Eventarea.objects.filter(id=eventarea_id).update(shape=shape_geom)
        return EventareaContext.get_by_id(eventarea_id)

    @staticmethod
    def delete(eventarea_id):
        """删除活动区域"""
        Eventarea.objects.filter(id=eventarea_id).delete()

    @staticmethod
    def delete_many(eventarea_ids):
        """批量删除活动区域"""
        if eventarea_ids:
            Eventarea.objects.filter(id__in=eventarea_ids).delete()


class OtherareaContext:
    """
    其他区域（Otherarea）的数据访问层
    负责与数据库交互，提供基本的CRUD操作
    """

    @staticmethod
    def get_all():
        """获取所有其他区域"""
        return Otherarea.objects.all()

    @staticmethod
    def get_by_id(otherarea_id):
        """根据ID获取其他区域"""
        return Otherarea.objects.filter(id=otherarea_id).first()

    @staticmethod
    def create(shape, map_id=None, type_val=None):
        """创建新的其他区域，并可选绑定到指定地图"""
        # 将shape字符串转换为GEOSGeometry对象，支持WKT和GeoJSON格式
        try:
            # 直接解析，并明确指定SRID=2385
            shape_geom = GEOSGeometry(shape, srid=2385)
        except Exception as e:
            raise ValueError(f"Invalid spatial data. Failed to parse geometry: {str(e)}")
        
        # 确保SRID为2385（双重保险）
        if shape_geom.srid != 2385:
            shape_geom.srid = 2385
        
        otherarea = Otherarea.objects.create(
            shape=shape_geom,
            type=type_val if type_val is not None else 0  # 默认 0，避免 NOT NULL 约束报错
        )
        if map_id is not None:
            OtherareaMap.objects.create(otherarea=otherarea, map_id=map_id)
        return otherarea

    @staticmethod
    def update_shape(otherarea_id, shape):
        """更新其他区域的形状"""
        # 将shape字符串转换为GEOSGeometry对象，支持WKT和GeoJSON格式
        try:
            # 直接解析，并明确指定SRID=2385
            shape_geom = GEOSGeometry(shape, srid=2385)
        except Exception as e:
            raise ValueError(f"Invalid spatial data. Failed to parse geometry: {str(e)}")
        
        # 确保SRID为2385（双重保险）
        if shape_geom.srid != 2385:
            shape_geom.srid = 2385
        
        Otherarea.objects.filter(id=otherarea_id).update(shape=shape_geom)
        return OtherareaContext.get_by_id(otherarea_id)

    @staticmethod
    def delete(otherarea_id):
        """删除其他区域"""
        Otherarea.objects.filter(id=otherarea_id).delete()

    @staticmethod
    def delete_many(otherarea_ids):
        """批量删除其他区域"""
        if otherarea_ids:
            Otherarea.objects.filter(id__in=otherarea_ids).delete()


class FacilityContext:
    """
    设施（Facility）的数据访问层
    """

    @staticmethod
    def get_all():
        return Facility.objects.all()

    @staticmethod
    def get_by_id(facility_id):
        return Facility.objects.filter(id=facility_id).first()

    @staticmethod
    def create(location, map_id=None, type_val=None):
        try:
            loc_geom = GEOSGeometry(location)
            if loc_geom.srid != 2385:
                loc_geom.srid = 2385
        except Exception as e:
            raise ValueError(f"Invalid spatial data: {str(e)}")

        facility = Facility.objects.create(
            location=loc_geom,
            type=type_val if type_val is not None else 0
        )
        if map_id is not None:
            FacilityMap.objects.create(facility=facility, map_id=map_id)
        return facility

    @staticmethod
    def update_location(facility_id, location):
        """更新设施位置"""
        try:
            loc_geom = GEOSGeometry(location)
            if loc_geom.srid != 2385:
                loc_geom.srid = 2385
        except Exception as e:
            raise ValueError(f"Invalid spatial data: {str(e)}")

        Facility.objects.filter(id=facility_id).update(location=loc_geom)
        return FacilityContext.get_by_id(facility_id)

    @staticmethod
    def delete(facility_id):
        Facility.objects.filter(id=facility_id).delete()

    @staticmethod
    def delete_many(facility_ids):
        """批量删除设施"""
        if facility_ids:
            Facility.objects.filter(id__in=facility_ids).delete()