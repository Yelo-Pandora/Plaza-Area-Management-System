# Create your models here.
from core.context import BaseContext
from core.models import Admin


class AdminContext(BaseContext):
    """针对 Admin 模型的基础 CRUD 和查询操作"""
    def __init__(self):
        super().__init__(Admin)

    def get_by_account(self, account: str) -> Admin | None:
        """根据账号名获取 Admin 实例"""
        try:
            return self.model.objects.get(account=account)
        except self.model.DoesNotExist:
            return None