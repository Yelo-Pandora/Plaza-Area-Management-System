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


def get_eventarea_serializer():
    Eventarea = apps.get_model('core', 'Eventarea')

    class EventareaSerializer(serializers.ModelSerializer):
        class Meta:
            model = Eventarea
            fields = '__all__'

    return EventareaSerializer


def get_facility_serializer():
    Facility = apps.get_model('core', 'Facility')

    class FacilitySerializer(serializers.ModelSerializer):
        class Meta:
            model = Facility
            fields = '__all__'

    return FacilitySerializer


def get_otherarea_serializer():
    Otherarea = apps.get_model('core', 'Otherarea')

    class OtherareaSerializer(serializers.ModelSerializer):
        class Meta:
            model = Otherarea
            fields = '__all__'

    return OtherareaSerializer


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


def get_simple_eventarea_serializer():
    Eventarea = apps.get_model('core', 'Eventarea')

    class SimpleEventareaSerializer(serializers.ModelSerializer):
        class Meta:
            model = Eventarea
            fields = ['id', 'organizer_name', 'type']

    return SimpleEventareaSerializer


def get_simple_facility_serializer():
    Facility = apps.get_model('core', 'Facility')

    class SimpleFacilitySerializer(serializers.ModelSerializer):
        class Meta:
            model = Facility
            fields = ['id', 'type']

    return SimpleFacilitySerializer


def get_simple_otherarea_serializer():
    Otherarea = apps.get_model('core', 'Otherarea')

    class SimpleOtherareaSerializer(serializers.ModelSerializer):
        class Meta:
            model = Otherarea
            fields = ['id', 'type', 'is_public']

    return SimpleOtherareaSerializer