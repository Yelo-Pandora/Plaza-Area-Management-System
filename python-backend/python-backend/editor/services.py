from .context import StoreareaContext, EventContext, EventareaContext, OtherareaContext,FacilityContext


class StoreareaService:
    """
    店铺区域（Storearea）的业务层
    负责处理业务逻辑，调用数据访问层方法，仅处理shape属性相关操作
    """

    @staticmethod
    def get_all_storeareas():
        """获取所有店铺区域"""
        return StoreareaContext.get_all()

    @staticmethod
    def get_storearea_by_id(storearea_id):
        """根据ID获取店铺区域"""
        return StoreareaContext.get_by_id(storearea_id)

    @staticmethod
    def create_storearea(shape, map_id=None):
        """创建新的店铺区域，并可选绑定到指定地图"""
        return StoreareaContext.create(shape, map_id)

    @staticmethod
    def update_shape(storearea_id, shape):
        """更新店铺区域的形状"""
        # 可以在这里添加业务逻辑验证
        return StoreareaContext.update_shape(storearea_id, shape)

    @staticmethod
    def delete_storearea(storearea_id):
        """删除店铺区域"""
        # 可以在这里添加业务逻辑验证
        return StoreareaContext.delete(storearea_id)

    @staticmethod
    def get_events_for_storearea(storearea_id):
        """获取店铺关联的所有活动ID"""
        return StoreareaContext.get_events_by_storearea(storearea_id)


class EventService:
    """
    活动（Event）的业务层
    负责处理业务逻辑，调用数据访问层方法，仅处理shape属性相关操作
    """

    @staticmethod
    def get_all_events():
        """获取所有活动"""
        return EventContext.get_all()

    @staticmethod
    def get_event_by_id(event_id):
        """根据ID获取活动"""
        return EventContext.get_by_id(event_id)



    @staticmethod
    def get_areas_for_event(event_id):
        """获取活动关联的所有区域ID（包括店铺区域和活动区域）"""
        storearea_ids = EventContext.get_storeareas_by_event(event_id)
        eventarea_ids = EventContext.get_eventareas_by_event(event_id)
        return {
            'storearea_ids': storearea_ids,
            'eventarea_ids': eventarea_ids,
            'all_area_ids': storearea_ids + eventarea_ids
        }

    @staticmethod
    def add_storearea_to_event(event_id, storearea_id):
        """添加活动与店铺区域的关联关系"""
        # 可以在这里添加业务逻辑验证（如检查活动和店铺是否存在等）
        return EventContext.add_storearea_relation(event_id, storearea_id)

    @staticmethod
    def remove_storearea_from_event(event_id, storearea_id):
        """移除活动与店铺区域的关联关系"""
        # 可以在这里添加业务逻辑验证
        return EventContext.remove_storearea_relation(event_id, storearea_id)

    @staticmethod
    def add_eventarea_to_event(event_id, eventarea_id):
        """添加活动与活动区域的关联关系"""
        # 可以在这里添加业务逻辑验证（如检查活动和活动区域是否存在等）
        return EventContext.add_eventarea_relation(event_id, eventarea_id)

    @staticmethod
    def remove_eventarea_from_event(event_id, eventarea_id):
        """移除活动与活动区域的关联关系"""
        # 可以在这里添加业务逻辑验证
        return EventContext.remove_eventarea_relation(event_id, eventarea_id)


class EventareaService:
    """
    活动区域（Eventarea）的业务层
    负责处理业务逻辑，调用数据访问层方法
    注意：在editor模块中只处理shape属性的更新
    """

    @staticmethod
    def get_all_eventareas():
        """获取所有活动区域"""
        return EventareaContext.get_all()

    @staticmethod
    def get_eventarea_by_id(eventarea_id):
        """根据ID获取活动区域"""
        return EventareaContext.get_by_id(eventarea_id)

    @staticmethod
    def create_eventarea(shape, map_id=None):
        """创建新的活动区域，并可选绑定到指定地图"""
        return EventareaContext.create(shape, map_id)

    @staticmethod
    def update_eventarea_shape(eventarea_id, shape):
        """更新活动区域的形状"""
        # 可以在这里添加业务逻辑验证（如形状有效性检查等）
        return EventareaContext.update_shape(eventarea_id, shape)

    @staticmethod
    def delete_eventarea(eventarea_id):
        """删除活动区域"""
        # 可以在这里添加业务逻辑验证
        return EventareaContext.delete(eventarea_id)


class OtherareaService:
    """
    其他区域（Otherarea）的业务层
    负责处理业务逻辑，调用数据访问层方法
    注意：在editor模块中只处理shape属性的更新
    """

    @staticmethod
    def get_all_otherareas():
        """获取所有其他区域"""
        return OtherareaContext.get_all()

    @staticmethod
    def get_otherarea_by_id(otherarea_id):
        """根据ID获取其他区域"""
        return OtherareaContext.get_by_id(otherarea_id)

    @staticmethod
    def create_otherarea(shape, map_id=None, type_val=None):
        """创建新的其他区域，并可选绑定到指定地图"""
        return OtherareaContext.create(shape, map_id, type_val)

    @staticmethod
    def update_otherarea_shape(otherarea_id, shape):
        """更新其他区域的形状"""
        # 可以在这里添加业务逻辑验证（如形状有效性检查等）
        return OtherareaContext.update_shape(otherarea_id, shape)

    @staticmethod
    def delete_otherarea(otherarea_id):
        """删除其他区域"""
        # 可以在这里添加业务逻辑验证
        return OtherareaContext.delete(otherarea_id)

class FacilityService:
    """
    设施（Facility）的业务层
    """
    @staticmethod
    def get_all_facilities():
        return FacilityContext.get_all()

    @staticmethod
    def get_facility_by_id(facility_id):
        return FacilityContext.get_by_id(facility_id)

    @staticmethod
    def create_facility(location, map_id=None, type_val=None):
        return FacilityContext.create(location, map_id, type_val)

    @staticmethod
    def update_facility_location(facility_id, location):
        return FacilityContext.update_location(facility_id, location)

    @staticmethod
    def delete_facility(facility_id):
        return FacilityContext.delete(facility_id)