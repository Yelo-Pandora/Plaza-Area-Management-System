from rest_framework import serializers
from django.apps import apps


def get_storearea_serializer():
    """获取 Storearea 序列化器"""
    Storearea = apps.get_model('core', 'Storearea')

    class StoreareaSerializer(serializers.ModelSerializer):
        class Meta:
            model = Storearea
            fields = '__all__'
            # 由于使用了 managed=False，需要明确指定字段
            # 但 ModelSerializer 会自动从模型获取字段

    return StoreareaSerializer


def get_event_serializer():
    """获取 Event 序列化器"""
    Event = apps.get_model('core', 'Event')

    class EventSerializer(serializers.ModelSerializer):
        class Meta:
            model = Event
            fields = '__all__'

    return EventSerializer


def get_eventarea_serializer():
    """获取活动区域序列化器"""
    Eventarea = apps.get_model('core', 'Eventarea')
    
    class EventareaSerializer(serializers.ModelSerializer):
        class Meta:
            model = Eventarea
            fields = '__all__'
    
    return EventareaSerializer


def get_otherarea_serializer():
    """获取其他区域序列化器"""
    Otherarea = apps.get_model('core', 'Otherarea')
    
    class OtherareaSerializer(serializers.ModelSerializer):
        class Meta:
            model = Otherarea
            fields = '__all__'
    
    return OtherareaSerializer
