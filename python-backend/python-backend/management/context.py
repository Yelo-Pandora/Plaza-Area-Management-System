from core.models import Eventarea, Otherarea, Event, Storearea


class EventareaContext:
    """
    活动区域（Eventarea）的数据访问层
    
    提供与Eventarea模型相关的数据操作方法
    """
    
    @staticmethod
    def get_all_eventareas():
        """
        获取所有活动区域
        
        Returns:
            QuerySet: 活动区域的查询集
        """
        return Eventarea.objects.all()
    
    @staticmethod
    def get_eventarea_by_id(eventarea_id):
        """
        根据ID获取活动区域
        
        Args:
            eventarea_id: 活动区域ID
        
        Returns:
            Eventarea: 活动区域对象
        """
        return Eventarea.objects.get(id=eventarea_id)
    
    @staticmethod
    def create_eventarea(data):
        """
        创建新的活动区域
        
        Args:
            data: 活动区域数据
        
        Returns:
            Eventarea: 创建的活动区域对象
        """
        return Eventarea.objects.create(**data)
    
    @staticmethod
    def update_eventarea(eventarea_id, data):
        """
        更新活动区域
        
        Args:
            eventarea_id: 活动区域ID
            data: 更新数据
        
        Returns:
            Eventarea: 更新后的活动区域对象
        """
        eventarea = Eventarea.objects.get(id=eventarea_id)
        for key, value in data.items():
            setattr(eventarea, key, value)
        eventarea.save()
        return eventarea
    
    @staticmethod
    def delete_eventarea(eventarea_id):
        """
        删除活动区域
        
        Args:
            eventarea_id: 活动区域ID
        """
        Eventarea.objects.filter(id=eventarea_id).delete()


class EventContext:
    """
    活动（Event）的数据访问层
    
    提供与Event模型相关的数据操作方法
    注意：不处理shape属性，该属性由editor模块处理
    """
    
    @staticmethod
    def get_all_events():
        """
        获取所有活动
        
        Returns:
            QuerySet: 活动的查询集
        """
        return Event.objects.all()
    
    @staticmethod
    def get_event_by_id(event_id):
        """
        根据ID获取活动
        
        Args:
            event_id: 活动ID
        
        Returns:
            Event: 活动对象
        """
        return Event.objects.get(id=event_id)
    
    @staticmethod
    def create_event(data):
        """
        创建新的活动
        
        Args:
            data: 活动数据
        
        Returns:
            Event: 创建的活动对象
        """
        return Event.objects.create(**data)
    
    @staticmethod
    def update_event(event_id, data):
        """
        更新活动
        
        Args:
            event_id: 活动ID
            data: 更新数据
        
        Returns:
            Event: 更新后的活动对象
        """
        event = Event.objects.get(id=event_id)
        for key, value in data.items():
            setattr(event, key, value)
        event.save()
        return event
    
    @staticmethod
    def delete_event(event_id):
        """
        删除活动
        
        Args:
            event_id: 活动ID
        """
        Event.objects.filter(id=event_id).delete()


class StoreareaContext:
    """
    店铺区域（Storearea）的数据访问层
    
    提供与Storearea模型相关的数据操作方法
    注意：不处理shape属性，该属性由editor模块处理
    """
    
    @staticmethod
    def get_all_storeareas():
        """
        获取所有店铺区域
        
        Returns:
            QuerySet: 店铺区域的查询集
        """
        return Storearea.objects.all()
    
    @staticmethod
    def get_storearea_by_id(storearea_id):
        """
        根据ID获取店铺区域
        
        Args:
            storearea_id: 店铺区域ID
        
        Returns:
            Storearea: 店铺区域对象
        """
        return Storearea.objects.get(id=storearea_id)
    
    @staticmethod
    def create_storearea(data):
        """
        创建新的店铺区域
        
        Args:
            data: 店铺区域数据
        
        Returns:
            Storearea: 创建的店铺区域对象
        """
        return Storearea.objects.create(**data)
    
    @staticmethod
    def update_storearea(storearea_id, data):
        """
        更新店铺区域
        
        Args:
            storearea_id: 店铺区域ID
            data: 更新数据
        
        Returns:
            Storearea: 更新后的店铺区域对象
        """
        storearea = Storearea.objects.get(id=storearea_id)
        for key, value in data.items():
            setattr(storearea, key, value)
        storearea.save()
        return storearea
    
    @staticmethod
    def delete_storearea(storearea_id):
        """
        删除店铺区域
        
        Args:
            storearea_id: 店铺区域ID
        """
        Storearea.objects.filter(id=storearea_id).delete()


class OtherareaContext:
    """
    其他区域（Otherarea）的数据访问层
    
    提供与Otherarea模型相关的数据操作方法
    """
    
    @staticmethod
    def get_all_otherareas():
        """
        获取所有其他区域
        
        Returns:
            QuerySet: 其他区域的查询集
        """
        return Otherarea.objects.all()
    
    @staticmethod
    def get_otherarea_by_id(otherarea_id):
        """
        根据ID获取其他区域
        
        Args:
            otherarea_id: 其他区域ID
        
        Returns:
            Otherarea: 其他区域对象
        """
        return Otherarea.objects.get(id=otherarea_id)
    
    @staticmethod
    def create_otherarea(data):
        """
        创建新的其他区域
        
        Args:
            data: 其他区域数据
        
        Returns:
            Otherarea: 创建的其他区域对象
        """
        return Otherarea.objects.create(**data)
    
    @staticmethod
    def update_otherarea(otherarea_id, data):
        """
        更新其他区域
        
        Args:
            otherarea_id: 其他区域ID
            data: 更新数据
        
        Returns:
            Otherarea: 更新后的其他区域对象
        """
        otherarea = Otherarea.objects.get(id=otherarea_id)
        for key, value in data.items():
            setattr(otherarea, key, value)
        otherarea.save()
        return otherarea
    
    @staticmethod
    def delete_otherarea(otherarea_id):
        """
        删除其他区域
        
        Args:
            otherarea_id: 其他区域ID
        """
        Otherarea.objects.filter(id=otherarea_id).delete()