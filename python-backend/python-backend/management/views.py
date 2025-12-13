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