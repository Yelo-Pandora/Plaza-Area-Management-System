from rest_framework import serializers
from django.apps import apps


# 使用延迟加载的方式定义序列化器
def get_storearea_serializer():
    Storearea = apps.get_model('core', 'Storearea')

    class StoreareaSerializer(serializers.ModelSerializer):
        class Meta:
            model = Storearea
            fields = '__all__'

    return StoreareaSerializer


def get_event_serializer():
    Event = apps.get_model('core', 'Event')

    class EventSerializer(serializers.ModelSerializer):
        class Meta:
            model = Event
            fields = '__all__'

    return EventSerializer


def get_simple_storearea_serializer():
    Storearea = apps.get_model('core', 'Storearea')

    class SimpleStoreareaSerializer(serializers.ModelSerializer):
        class Meta:
            model = Storearea
            fields = ['id', 'store_name', 'type']

    return SimpleStoreareaSerializer


def get_simple_event_serializer():
    Event = apps.get_model('core', 'Event')

    class SimpleEventSerializer(serializers.ModelSerializer):
        class Meta:
            model = Event
            fields = ['id', 'event_name', 'start_date', 'end_date']

    return SimpleEventSerializer