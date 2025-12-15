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
