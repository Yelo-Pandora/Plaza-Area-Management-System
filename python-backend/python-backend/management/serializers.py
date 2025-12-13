from rest_framework import serializers
from core.models import Admin

# Input Serializers (用于接收前端数据)
class AdminRegisterSerializer(serializers.Serializer):
    """管理员注册输入"""
    account = serializers.CharField(max_length=64)
    password = serializers.CharField(max_length=128, write_only=True)
    name = serializers.CharField(max_length=64, required=False, allow_blank=True)

class AdminLoginSerializer(serializers.Serializer):
    """管理员登录输入"""
    account = serializers.CharField(max_length=64)
    password = serializers.CharField(max_length=128, write_only=True) # write_only: 密码只用于输入，不用于输出

class AdminUpdateSerializer(serializers.Serializer):
    """管理员修改信息输入 (用于 PUT / PATCH)"""
    name = serializers.CharField(max_length=64, required=False, allow_blank=True)
    # 允许修改密码，但必须使用新的字段名 new_password
    new_password = serializers.CharField(max_length=128, required=False, write_only=True)

# Output Serializer (用于返回 Admin 实例信息)
class AdminProfileSerializer(serializers.ModelSerializer):
    """管理员信息的输出格式 (不暴露密码)"""
    class Meta:
        model = Admin
        fields = ['id', 'account', 'name']
        read_only_fields = ['id', 'account'] # 账号和ID不能通过这个接口修改