from rest_framework import serializers
from django.apps import apps


def get_eventarea_serializer():
    """获取活动区域序列化器"""
    Eventarea = apps.get_model('core', 'Eventarea')
    
    class EventareaSerializer(serializers.ModelSerializer):
        class Meta:
            model = Eventarea
            exclude = ['shape']
    
    return EventareaSerializer


def get_otherarea_serializer():
    """获取其他区域序列化器"""
    Otherarea = apps.get_model('core', 'Otherarea')
    
    class OtherareaSerializer(serializers.ModelSerializer):
        class Meta:
            model = Otherarea
            exclude = ['shape']
    
    return OtherareaSerializer


def get_event_serializer():
    """获取Event模型的序列化器"""
    Event = apps.get_model('core', 'Event')
    
    class EventSerializer(serializers.ModelSerializer):
        class Meta:
            model = Event
            fields = '__all__'
    
    return EventSerializer


def get_storearea_serializer():
    """获取Storearea模型的序列化器"""
    Storearea = apps.get_model('core', 'Storearea')
    
    class StoreareaSerializer(serializers.ModelSerializer):
        class Meta:
            model = Storearea
            exclude = ['shape']
    
    return StoreareaSerializer
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