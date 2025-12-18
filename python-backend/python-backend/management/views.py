from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import get_eventarea_serializer, get_otherarea_serializer, get_event_serializer, get_storearea_serializer, get_facility_serializer
from .services import EventareaService, OtherareaService, EventService, StoreareaService, FacilityService


class EventareaViewSet(viewsets.ModelViewSet):
    """
    活动区域（Eventarea）的视图集
    
    注意：
    - 在management模块中处理除shape属性外的所有其他属性
    - shape属性的操作由editor模块处理
    - 不允许修改shape属性
    
    支持的操作：
    - GET /api/management/eventarea/ - 获取所有活动区域列表
    - GET /api/management/eventarea/{id}/ - 获取指定活动区域详情
    - POST /api/management/eventarea/ - 创建新的活动区域
    - PUT /api/management/eventarea/{id}/ - 完整更新活动区域（不包括shape）
    - PATCH /api/management/eventarea/{id}/ - 部分更新活动区域（不包括shape）
    - DELETE /api/management/eventarea/{id}/ - 删除指定活动区域
    """
    
    def get_serializer_class(self):
        """获取序列化器类"""
        return get_eventarea_serializer()
    
    def get_queryset(self):
        """获取所有活动区域"""
        return EventareaService.get_all_eventareas()
    
    def list(self, request, *args, **kwargs):
        """获取所有活动区域列表"""
        eventareas = EventareaService.get_all_eventareas()
        serializer = self.get_serializer(eventareas, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """获取指定活动区域详情"""
        eventarea = get_object_or_404(EventareaService.get_all_eventareas(), pk=pk)
        serializer = self.get_serializer(eventarea)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建新的活动区域"""
        try:
            # 检查是否包含shape属性，如果包含则移除
            data = request.data.copy()
            if 'shape' in data:
                data.pop('shape')
            
            eventarea = EventareaService.create_eventarea(data)
            serializer = self.get_serializer(eventarea)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """完整更新活动区域（不包括shape）"""
        try:
            # 检查是否包含shape属性，如果包含则返回错误
            if 'shape' in request.data:
                return Response(
                    {'error': 'Shape attribute cannot be updated in management module'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            eventarea = EventareaService.update_eventarea(pk, request.data)
            serializer = self.get_serializer(eventarea)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, pk=None):
        """部分更新活动区域（不包括shape）"""
        try:
            # 检查是否包含shape属性，如果包含则返回错误
            if 'shape' in request.data:
                return Response(
                    {'error': 'Shape attribute cannot be updated in management module'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            eventarea = EventareaService.update_eventarea(pk, request.data)
            serializer = self.get_serializer(eventarea)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除指定活动区域"""
        try:
            EventareaService.delete_eventarea(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OtherareaViewSet(viewsets.ModelViewSet):
    """
    其他区域（Otherarea）的视图集
    
    注意：
    - 在management模块中处理除shape属性外的所有其他属性
    - shape属性的操作由editor模块处理
    - 不允许修改shape属性
    
    支持的操作：
    - GET /api/management/otherarea/ - 获取所有其他区域列表
    - GET /api/management/otherarea/{id}/ - 获取指定其他区域详情
    - POST /api/management/otherarea/ - 创建新的其他区域
    - PUT /api/management/otherarea/{id}/ - 完整更新其他区域（不包括shape）
    - PATCH /api/management/otherarea/{id}/ - 部分更新其他区域（不包括shape）
    - DELETE /api/management/otherarea/{id}/ - 删除指定其他区域
    """
    
    def get_serializer_class(self):
        """获取序列化器类"""
        return get_otherarea_serializer()
    
    def get_queryset(self):
        """获取所有其他区域"""
        return OtherareaService.get_all_otherareas()
    
    def list(self, request, *args, **kwargs):
        """获取所有其他区域列表"""
        otherareas = OtherareaService.get_all_otherareas()
        serializer = self.get_serializer(otherareas, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """获取指定其他区域详情"""
        otherarea = get_object_or_404(OtherareaService.get_all_otherareas(), pk=pk)
        serializer = self.get_serializer(otherarea)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建新的其他区域"""
        try:
            # 检查是否包含shape属性，如果包含则移除
            data = request.data.copy()
            if 'shape' in data:
                data.pop('shape')
            
            otherarea = OtherareaService.create_otherarea(data)
            serializer = self.get_serializer(otherarea)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """完整更新其他区域（不包括shape）"""
        try:
            # 检查是否包含shape属性，如果包含则返回错误
            if 'shape' in request.data:
                return Response(
                    {'error': 'Shape attribute cannot be updated in management module'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            otherarea = OtherareaService.update_otherarea(pk, request.data)
            serializer = self.get_serializer(otherarea)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, pk=None):
        """部分更新其他区域（不包括shape）"""
        try:
            # 检查是否包含shape属性，如果包含则返回错误
            if 'shape' in request.data:
                return Response(
                    {'error': 'Shape attribute cannot be updated in management module'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            otherarea = OtherareaService.update_otherarea(pk, request.data)
            serializer = self.get_serializer(otherarea)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除指定其他区域"""
        try:
            OtherareaService.delete_otherarea(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EventViewSet(viewsets.ModelViewSet):
    """
    活动（Event）的视图集
    
    支持的操作：
    - GET /api/management/event/ - 获取所有活动列表
    - GET /api/management/event/{id}/ - 获取指定活动详情
    - POST /api/management/event/ - 创建新的活动
    - PUT /api/management/event/{id}/ - 完整更新活动
    - PATCH /api/management/event/{id}/ - 部分更新活动
    - DELETE /api/management/event/{id}/ - 删除指定活动
    """
    
    def get_serializer_class(self):
        """获取序列化器类"""
        return get_event_serializer()
    
    def get_queryset(self):
        """获取所有活动"""
        return EventService.get_all_events()
    
    def list(self, request, *args, **kwargs):
        """获取所有活动列表"""
        events = EventService.get_all_events()
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """获取指定活动详情"""
        event = get_object_or_404(EventService.get_all_events(), pk=pk)
        serializer = self.get_serializer(event)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建新的活动"""
        try:
            event = EventService.create_event(request.data)
            serializer = self.get_serializer(event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """完整更新活动"""
        try:
            event = EventService.update_event(pk, request.data)
            serializer = self.get_serializer(event)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, pk=None):
        """部分更新活动"""
        try:
            event = EventService.update_event(pk, request.data)
            serializer = self.get_serializer(event)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除指定活动"""
        try:
            EventService.delete_event(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StoreareaViewSet(viewsets.ModelViewSet):
    """
    店铺区域（Storearea）的视图集
    
    注意：
    - 不处理shape属性，该属性由editor模块处理
    
    支持的操作：
    - GET /api/management/storearea/ - 获取所有店铺区域列表
    - GET /api/management/storearea/{id}/ - 获取指定店铺区域详情
    - POST /api/management/storearea/ - 创建新的店铺区域
    - PUT /api/management/storearea/{id}/ - 完整更新店铺区域（不包括shape）
    - PATCH /api/management/storearea/{id}/ - 部分更新店铺区域（不包括shape）
    - DELETE /api/management/storearea/{id}/ - 删除指定店铺区域
    """
    
    def get_serializer_class(self):
        """获取序列化器类"""
        return get_storearea_serializer()
    
    def get_queryset(self):
        """获取所有店铺区域"""
        return StoreareaService.get_all_storeareas()
    
    def list(self, request, *args, **kwargs):
        """获取所有店铺区域列表"""
        storeareas = StoreareaService.get_all_storeareas()
        serializer = self.get_serializer(storeareas, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """获取指定店铺区域详情"""
        storearea = get_object_or_404(StoreareaService.get_all_storeareas(), pk=pk)
        serializer = self.get_serializer(storearea)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建新的店铺区域"""
        try:
            # 检查是否包含shape属性，如果包含则移除
            data = request.data.copy()
            if 'shape' in data:
                data.pop('shape')
            
            storearea = StoreareaService.create_storearea(data)
            serializer = self.get_serializer(storearea)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """完整更新店铺区域（不包括shape）"""
        try:
            # 检查是否包含shape属性，如果包含则返回错误
            if 'shape' in request.data:
                return Response(
                    {'error': 'Shape attribute cannot be updated in management module'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            storearea = StoreareaService.update_storearea(pk, request.data)
            serializer = self.get_serializer(storearea)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, pk=None):
        """部分更新店铺区域（不包括shape）"""
        try:
            # 检查是否包含shape属性，如果包含则返回错误
            if 'shape' in request.data:
                return Response(
                    {'error': 'Shape attribute cannot be updated in management module'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            storearea = StoreareaService.update_storearea(pk, request.data)
            serializer = self.get_serializer(storearea)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """
        删除指定店铺区域
        """
        try:
            StoreareaService.delete_storearea(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FacilityViewSet(viewsets.ModelViewSet):
    """
    设施（Facility）的视图集
    
    注意：
    - 在management模块中处理除location属性外的所有其他属性
    - location属性的操作由editor模块处理
    - 不允许修改location属性
    
    支持的操作：
    - GET /api/management/facility/ - 获取所有设施列表
    - GET /api/management/facility/{id}/ - 获取指定设施详情
    - POST /api/management/facility/ - 创建新的设施
    - PUT /api/management/facility/{id}/ - 完整更新设施（不包括location）
    - PATCH /api/management/facility/{id}/ - 部分更新设施（不包括location）
    - DELETE /api/management/facility/{id}/ - 删除指定设施
    """
    
    def get_serializer_class(self):
        """获取序列化器类"""
        return get_facility_serializer()
    
    def get_queryset(self):
        """获取所有设施"""
        return FacilityService.get_all_facilities()
    
    def list(self, request, *args, **kwargs):
        """获取所有设施列表"""
        facilities = FacilityService.get_all_facilities()
        serializer = self.get_serializer(facilities, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """获取指定设施详情"""
        facility = get_object_or_404(FacilityService.get_all_facilities(), pk=pk)
        serializer = self.get_serializer(facility)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建新的设施"""
        try:
            # 检查是否包含location属性，如果包含则移除
            data = request.data.copy()
            if 'location' in data:
                data.pop('location')
            
            facility = FacilityService.create_facility(data)
            serializer = self.get_serializer(facility)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """完整更新设施（不包括location）"""
        try:
            # 检查是否包含location属性，如果包含则返回错误
            if 'location' in request.data:
                return Response(
                    {'error': 'Location attribute cannot be updated in management module'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            facility = FacilityService.update_facility(pk, request.data)
            serializer = self.get_serializer(facility)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, pk=None):
        """部分更新设施（不包括location）"""
        try:
            # 检查是否包含location属性，如果包含则返回错误
            if 'location' in request.data:
                return Response(
                    {'error': 'Location attribute cannot be updated in management module'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            facility = FacilityService.update_facility(pk, request.data)
            serializer = self.get_serializer(facility)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除指定设施"""
        try:
            FacilityService.delete_facility(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.http import HttpRequest

from .services import AdminService
from .serializers import AdminRegisterSerializer, AdminLoginSerializer, AdminUpdateSerializer, AdminProfileSerializer
from core.models import Admin
from core.context import BaseContext


class AdminAuthMixin:
    """一个简单的用于检查管理员登录状态并加载 Admin 实例的 Mixin"""
    @staticmethod
    def get_admin_user(request: HttpRequest) -> Admin | None:
        admin_id = request.session.get('admin_id')
        if admin_id:
            try:
                # 使用 BaseContext 或 AdminContext 获取实例
                return BaseContext(Admin).get_by_id(admin_id)
            except Admin.DoesNotExist:
                del request.session['admin_id']  # 清理过期会话
                return None
        return None


class AdminAuthView(APIView):
    """
    处理管理员的注册、登录、注销
    POST /api/management/auth/register/
    POST /api/management/auth/login/
    POST /api/management/auth/logout/
    """
    service_class = AdminService

    def post(self, request, action):
        service = self.service_class()

        if action == 'register':
            serializer = AdminRegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            try:
                admin = service.register_admin(**serializer.validated_data)
                return Response(AdminProfileSerializer(admin).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)

        elif action == 'login':
            serializer = AdminLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            admin = service.login_admin(**serializer.validated_data)

            if admin:
                # 登录成功：在 session 中设置 ID
                request.session['admin_id'] = admin.id
                return Response(AdminProfileSerializer(admin).data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid account or password"}, status=status.HTTP_401_UNAUTHORIZED)

        elif action == 'logout':
            if 'admin_id' in request.session:
                del request.session['admin_id']  # 清除 session
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)


# --- 个人信息接口 ---
class AdminProfileView(AdminAuthMixin, APIView):
    """
    处理管理员个人信息的获取和修改
    GET /api/management/profile/
    PUT/PATCH /api/management/profile/
    """
    service_class = AdminService
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin_user = None # 初始化实例属性
        
    def dispatch(self, request, *args, **kwargs):
        # 在处理请求前，先检查登录状态并加载 Admin 实例
        self.admin_user = self.get_admin_user(request)
        if not self.admin_user:
            return Response({"error": "Authentication credentials were not provided."},
                            status=status.HTTP_401_UNAUTHORIZED)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """获取当前登录管理员的个人信息"""
        # self.admin_user 已在 dispatch 中加载并验证
        return Response(AdminProfileSerializer(self.admin_user).data)

    def put(self, request):
        """修改当前登录管理员的个人信息 (PUT/PATCH 通用)"""
        serializer = AdminUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = self.service_class()

        updated_admin = service.update_profile(
            admin_instance=self.admin_user,
            name=serializer.validated_data.get('name'),
            new_password=serializer.validated_data.get('new_password')
        )

        return Response(AdminProfileSerializer(updated_admin).data, status=status.HTTP_200_OK)