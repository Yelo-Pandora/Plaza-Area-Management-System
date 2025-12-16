from .context import AdminContext
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