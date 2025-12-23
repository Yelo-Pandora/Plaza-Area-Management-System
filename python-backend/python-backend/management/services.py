from .context import EventareaContext, OtherareaContext, EventContext, StoreareaContext, FacilityContext
from core.models import Admin
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError


class AdminService:
    """负责管理员的注册、登录和个人信息修改的业务逻辑"""

    def __init__(self):
        self.ctx = AdminContext()

    def register_admin(self, account: str, password: str, name: str | None = None) -> Admin:
        """注册新管理员"""
        if self.ctx.get_by_account(account):
            raise ValidationError("Admin account already exists.")

        # 1. 密码哈希 (SECURITY CRITICAL)
        hashed_password = make_password(password)

        # 2. 创建实例
        admin_instance = self.ctx.create(
            account=account,
            password=hashed_password,
            name=name
        )
        return admin_instance

    def login_admin(self, account: str, password: str) -> Admin | None:
        """验证管理员登录凭证"""
        admin_instance = self.ctx.get_by_account(account)

        # 1. 检查实例是否存在
        if not admin_instance:
            return None  # 账号不存在

        # 2. 检查密码是否匹配 (使用 check_password 验证哈希值)
        if check_password(password, admin_instance.password):
            return admin_instance  # 登录成功

        return None  # 密码错误

    def update_profile(self, admin_instance: Admin, name: str | None, new_password: str | None) -> Admin:
        """更新管理员信息 (姓名和/或密码)"""
        update_data = {}

        if name is not None:
            update_data['name'] = name

        if new_password:
            # 3. 如果有新密码，哈希后再更新
            update_data['password'] = make_password(new_password)

        return self.ctx.update(admin_instance, **update_data)


class EventareaService:
    """
    活动区域（Eventarea）的业务逻辑层

    提供与Eventarea模型相关的业务逻辑处理方法
    注意：不处理shape属性，该属性由editor模块处理
    """

    @staticmethod
    def get_all_eventareas():
        """
        获取所有活动区域

        Returns:
            QuerySet: 活动区域的查询集
        """
        return EventareaContext.get_all_eventareas()

    @staticmethod
    def get_eventarea_by_id(eventarea_id):
        """
        根据ID获取活动区域

        Args:
            eventarea_id: 活动区域ID

        Returns:
            Eventarea: 活动区域对象
        """
        return EventareaContext.get_eventarea_by_id(eventarea_id)

    @staticmethod
    def create_eventarea(data):
        """
        创建新的活动区域

        Args:
            data: 活动区域数据

        Returns:
            Eventarea: 创建的活动区域对象
        """
        # 业务逻辑验证
        # 1. 验证数据完整性
        required_fields = ['is_active', 'description', 'organizer_name', 'organizer_phone', 'type']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Field '{field}' is required")

        # 2. 验证电话号码格式
        # 这里可以添加更复杂的电话号码验证逻辑
        if len(data['organizer_phone']) < 10:
            raise ValueError("Phone number must be at least 10 characters long")

        # 3. 验证类型是否合法
        valid_types = ['exhibition', 'concert', 'meeting', 'other']  # 根据实际需求调整
        if data['type'] not in valid_types:
            raise ValueError(f"Invalid type. Valid types are: {', '.join(valid_types)}")

        # 4. 如果提供了shape属性，将其移除（shape属性由editor模块处理）
        if 'shape' in data:
            data.pop('shape')

        return EventareaContext.create_eventarea(data)

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
        # 如果提供了shape属性，将其移除（shape属性由editor模块处理）
        if 'shape' in data:
            data.pop('shape')

        # 如果有其他业务逻辑验证，可以在这里添加

        return EventareaContext.update_eventarea(eventarea_id, data)

    @staticmethod
    def delete_eventarea(eventarea_id):
        """
        删除活动区域

        Args:
            eventarea_id: 活动区域ID
        """
        # 业务逻辑验证
        # 1. 验证活动区域是否存在
        eventarea = EventareaContext.get_eventarea_by_id(eventarea_id)

        # 2. 验证是否有相关联的活动
        if eventarea.event_set.exists():
            raise ValueError("Cannot delete eventarea with associated events")

        return EventareaContext.delete_eventarea(eventarea_id)


class OtherareaService:
    """
    其他区域（Otherarea）的业务逻辑层

    提供与Otherarea模型相关的业务逻辑处理方法
    注意：不处理shape属性，该属性由editor模块处理
    """

    @staticmethod
    def get_all_otherareas():
        """
        获取所有其他区域

        Returns:
            QuerySet: 其他区域的查询集
        """
        return OtherareaContext.get_all_otherareas()

    @staticmethod
    def get_otherarea_by_id(otherarea_id):
        """
        根据ID获取其他区域

        Args:
            otherarea_id: 其他区域ID

        Returns:
            Otherarea: 其他区域对象
        """
        return OtherareaContext.get_otherarea_by_id(otherarea_id)

    @staticmethod
    def create_otherarea(data):
        """
        创建新的其他区域

        Args:
            data: 其他区域数据

        Returns:
            Otherarea: 创建的其他区域对象
        """
        # 业务逻辑验证
        # 1. 验证数据完整性
        required_fields = ['is_active', 'description', 'type', 'is_public']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Field '{field}' is required")

        # 2. 验证类型是否合法
        valid_types = ['restroom', 'parking', 'entrance', 'exit', 'staircase', 'elevator', 'other']  # 根据实际需求调整
        if data['type'] not in valid_types:
            raise ValueError(f"Invalid type. Valid types are: {', '.join(valid_types)}")

        # 3. 如果提供了shape属性，将其移除（shape属性由editor模块处理）
        if 'shape' in data:
            data.pop('shape')

        return OtherareaContext.create_otherarea(data)

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
        # 如果提供了shape属性，将其移除（shape属性由editor模块处理）
        if 'shape' in data:
            data.pop('shape')

        # 如果有其他业务逻辑验证，可以在这里添加

        return OtherareaContext.update_otherarea(otherarea_id, data)

    @staticmethod
    def delete_otherarea(otherarea_id):
        """
        删除其他区域

        Args:
            otherarea_id: 其他区域ID
        """
        # 业务逻辑验证
        # 1. 验证其他区域是否存在
        otherarea = OtherareaContext.get_otherarea_by_id(otherarea_id)

        # 2. 可以添加其他验证逻辑

        return OtherareaContext.delete_otherarea(otherarea_id)


class EventService:
    """
    活动（Event）的业务逻辑层

    提供与Event模型相关的业务逻辑操作方法
    注意：不处理shape属性，该属性由editor模块处理
    """

    @staticmethod
    def get_all_events():
        """
        获取所有活动

        Returns:
            QuerySet: 活动的查询集
        """
        return EventContext.get_all_events()

    @staticmethod
    def get_event_by_id(event_id):
        """
        根据ID获取活动

        Args:
            event_id: 活动ID

        Returns:
            Event: 活动对象
        """
        return EventContext.get_event_by_id(event_id)

    @staticmethod
    def create_event(data):
        """
        创建新的活动

        Args:
            data: 活动数据

        Returns:
            Event: 创建的活动对象
        """
        # 移除可能存在的shape属性
        if 'shape' in data:
            del data['shape']

        # 业务逻辑验证
        # 这里可以添加更多的业务逻辑验证

        return EventContext.create_event(data)

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
        # 移除可能存在的shape属性
        if 'shape' in data:
            del data['shape']

        # 业务逻辑验证
        # 这里可以添加更多的业务逻辑验证

        return EventContext.update_event(event_id, data)

    @staticmethod
    def delete_event(event_id):
        """
        删除活动

        Args:
            event_id: 活动ID
        """
        EventContext.delete_event(event_id)


class StoreareaService:
    """
    店铺区域（Storearea）的业务逻辑层

    提供与Storearea模型相关的业务逻辑操作方法
    注意：不处理shape属性，该属性由editor模块处理
    """

    @staticmethod
    def get_all_storeareas():
        """
        获取所有店铺区域

        Returns:
            QuerySet: 店铺区域的查询集
        """
        return StoreareaContext.get_all_storeareas()

    @staticmethod
    def get_storearea_by_id(storearea_id):
        """
        根据ID获取店铺区域

        Args:
            storearea_id: 店铺区域ID

        Returns:
            Storearea: 店铺区域对象
        """
        return StoreareaContext.get_storearea_by_id(storearea_id)

    @staticmethod
    def create_storearea(data):
        """
        创建新的店铺区域

        Args:
            data: 店铺区域数据

        Returns:
            Storearea: 创建的店铺区域对象
        """
        # 移除可能存在的shape属性
        if 'shape' in data:
            del data['shape']

        # 业务逻辑验证
        # 这里可以添加更多的业务逻辑验证

        return StoreareaContext.create_storearea(data)

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
        # 移除可能存在的shape属性
        if 'shape' in data:
            del data['shape']

        # 业务逻辑验证
        # 这里可以添加更多的业务逻辑验证

        return StoreareaContext.update_storearea(storearea_id, data)

    @staticmethod
    def delete_storearea(storearea_id):
        """
        删除店铺区域
        
        Args:
            storearea_id: 店铺区域ID
        """
        StoreareaContext.delete_storearea(storearea_id)


class FacilityService:
    """
    设施（Facility）的业务逻辑层
    
    提供与Facility模型相关的业务逻辑处理方法
    注意：location属性由editor模块处理
    """

    @staticmethod
    def get_all_facilities():
        """
        获取所有设施
        
        Returns:
            QuerySet: 设施的查询集
        """
        return FacilityContext.get_all_facilities()

    @staticmethod
    def get_facility_by_id(facility_id):
        """
        根据ID获取设施
        
        Args:
            facility_id: 设施ID
        
        Returns:
            Facility: 设施对象
        """
        return FacilityContext.get_facility_by_id(facility_id)

    @staticmethod
    def create_facility(data):
        """
        创建新的设施
        
        Args:
            data: 设施数据
        
        Returns:
            Facility: 创建的设施对象
        """
        # 业务逻辑验证
        # 1. 验证数据完整性
        required_fields = ['is_active', 'description', 'type']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Field '{field}' is required")

        # 2. 验证类型是否合法（根据实际需求调整）
        # 这里假设type是整数类型，表示不同的设施类型

        # 3. 如果提供了location属性，将其移除（location属性由editor模块处理）
        if 'location' in data:
            data.pop('location')

        return FacilityContext.create_facility(data)

    @staticmethod
    def update_facility(facility_id, data):
        """
        更新设施
        
        Args:
            facility_id: 设施ID
            data: 更新数据
        
        Returns:
            Facility: 更新后的设施对象
        """
        # 如果提供了location属性，将其移除（location属性由editor模块处理）
        if 'location' in data:
            data.pop('location')

        # 如果有其他业务逻辑验证，可以在这里添加

        return FacilityContext.update_facility(facility_id, data)

    @staticmethod
    def delete_facility(facility_id):
        """
        删除设施
        
        Args:
            facility_id: 设施ID
        """
        # 业务逻辑验证
        # 1. 验证设施是否存在
        facility = FacilityContext.get_facility_by_id(facility_id)

        # 2. 可以添加其他验证逻辑

        return FacilityContext.delete_facility(facility_id)