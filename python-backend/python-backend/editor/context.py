from django.contrib.gis.geos import GEOSGeometry
from core.models import Event, Storearea, EventStorearea, EventEventarea, Eventarea, Otherarea


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
    def create(shape):
        """创建新的店铺区域"""
        # 将shape字符串转换为GEOSGeometry对象，支持WKT和GeoJSON格式
        try:
            # 尝试直接解析（支持WKT格式）
            shape_geom = GEOSGeometry(shape)
        except Exception as e:
            try:
                # 尝试解析GeoJSON格式
                import json
                geojson_data = json.loads(shape)
                shape_geom = GEOSGeometry(json.dumps(geojson_data))
            except Exception as e2:
                raise ValueError(f"Invalid spatial data. Both WKT and GeoJSON parsing failed: {str(e)}")
        
        storearea = Storearea.objects.create(shape=shape_geom)
        return storearea

    @staticmethod
    def update_shape(storearea_id, shape):
        """更新店铺区域的形状"""
        # 将shape字符串转换为GEOSGeometry对象，支持WKT和GeoJSON格式
        try:
            # 尝试直接解析（支持WKT格式）
            shape_geom = GEOSGeometry(shape)
        except Exception as e:
            try:
                # 尝试解析GeoJSON格式
                import json
                geojson_data = json.loads(shape)
                shape_geom = GEOSGeometry(json.dumps(geojson_data))
            except Exception as e2:
                raise ValueError(f"Invalid spatial data. Both WKT and GeoJSON parsing failed: {str(e)}")
        
        Storearea.objects.filter(id=storearea_id).update(shape=shape_geom)
        return StoreareaContext.get_by_id(storearea_id)

    @staticmethod
    def delete(storearea_id):
        """删除店铺区域"""
        Storearea.objects.filter(id=storearea_id).delete()

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
    def create(shape):
        """创建新的活动区域"""
        # 将shape字符串转换为GEOSGeometry对象，支持WKT和GeoJSON格式
        try:
            # 尝试直接解析（支持WKT格式）
            shape_geom = GEOSGeometry(shape)
        except Exception as e:
            try:
                # 尝试解析GeoJSON格式
                import json
                geojson_data = json.loads(shape)
                shape_geom = GEOSGeometry(json.dumps(geojson_data))
            except Exception as e2:
                raise ValueError(f"Invalid spatial data. Both WKT and GeoJSON parsing failed: {str(e)}")
        
        eventarea = Eventarea.objects.create(shape=shape_geom)
        return eventarea

    @staticmethod
    def update_shape(eventarea_id, shape):
        """更新活动区域的形状"""
        # 将shape字符串转换为GEOSGeometry对象，支持WKT和GeoJSON格式
        try:
            # 尝试直接解析（支持WKT格式）
            shape_geom = GEOSGeometry(shape)
        except Exception as e:
            try:
                # 尝试解析GeoJSON格式
                import json
                geojson_data = json.loads(shape)
                shape_geom = GEOSGeometry(json.dumps(geojson_data))
            except Exception as e2:
                raise ValueError(f"Invalid spatial data. Both WKT and GeoJSON parsing failed: {str(e)}")
        
        Eventarea.objects.filter(id=eventarea_id).update(shape=shape_geom)
        return EventareaContext.get_by_id(eventarea_id)

    @staticmethod
    def delete(eventarea_id):
        """删除活动区域"""
        Eventarea.objects.filter(id=eventarea_id).delete()


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
    def create(shape):
        """创建新的其他区域"""
        # 将shape字符串转换为GEOSGeometry对象，支持WKT和GeoJSON格式
        try:
            # 尝试直接解析（支持WKT格式）
            shape_geom = GEOSGeometry(shape)
        except Exception as e:
            try:
                # 尝试解析GeoJSON格式
                import json
                geojson_data = json.loads(shape)
                shape_geom = GEOSGeometry(json.dumps(geojson_data))
            except Exception as e2:
                raise ValueError(f"Invalid spatial data. Both WKT and GeoJSON parsing failed: {str(e)}")
        
        otherarea = Otherarea.objects.create(shape=shape_geom)
        return otherarea

    @staticmethod
    def update_shape(otherarea_id, shape):
        """更新其他区域的形状"""
        # 将shape字符串转换为GEOSGeometry对象，支持WKT和GeoJSON格式
        try:
            # 尝试直接解析（支持WKT格式）
            shape_geom = GEOSGeometry(shape)
        except Exception as e:
            try:
                # 尝试解析GeoJSON格式
                import json
                geojson_data = json.loads(shape)
                shape_geom = GEOSGeometry(json.dumps(geojson_data))
            except Exception as e2:
                raise ValueError(f"Invalid spatial data. Both WKT and GeoJSON parsing failed: {str(e)}")
        
        Otherarea.objects.filter(id=otherarea_id).update(shape=shape_geom)
        return OtherareaContext.get_by_id(otherarea_id)

    @staticmethod
    def delete(otherarea_id):
        """删除其他区域"""
        Otherarea.objects.filter(id=otherarea_id).delete()
