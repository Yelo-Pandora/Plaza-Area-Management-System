from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.apps import apps


# 在视图函数中动态获取序列化器
def get_serializer_class(model_name, serializer_type='default'):
    """动态获取序列化器类"""
    if model_name == 'Storearea' and serializer_type == 'default':
        from .serializers import get_storearea_serializer
        return get_storearea_serializer()
    elif model_name == 'Storearea' and serializer_type == 'simple':
        from .serializers import get_simple_storearea_serializer
        return get_simple_storearea_serializer()
    elif model_name == 'Event' and serializer_type == 'default':
        from .serializers import get_event_serializer
        return get_event_serializer()
    elif model_name == 'Event' and serializer_type == 'simple':
        from .serializers import get_simple_event_serializer
        return get_simple_event_serializer()


# Search店铺功能

@api_view(['GET'])
def storearea_by_id(request, storearea_id):
    """
    按ID寻找店铺区域
    """
    Storearea = apps.get_model('core', 'Storearea')
    StoreareaSerializer = get_serializer_class('Storearea', 'default')

    try:
        storearea = Storearea.objects.get(id=storearea_id)
        serializer = StoreareaSerializer(storearea)
        return Response(serializer.data)
    except Storearea.DoesNotExist:
        return Response(
            {'error': 'Storearea not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def storearea_search(request):
    """
    按名称寻找店铺区域
    """
    Storearea = apps.get_model('core', 'Storearea')
    StoreareaSerializer = get_serializer_class('Storearea', 'default')

    name = request.GET.get('name', '').strip()
    if not name:
        return Response(
            {'error': 'Name parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    storeareas = Storearea.objects.filter(
        store_name__icontains=name,
        is_active=True
    )
    serializer = StoreareaSerializer(storeareas, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def storearea_list_by_type(request):
    """
    返回指定类型店铺区域列表
    """
    Storearea = apps.get_model('core', 'Storearea')
    SimpleStoreareaSerializer = get_serializer_class('Storearea', 'simple')

    type_param = request.GET.get('type', '').strip()

    if type_param:
        try:
            type_id = int(type_param)
            storeareas = Storearea.objects.filter(type=type_id, is_active=True)
            StoreareaSerializer = get_serializer_class('Storearea', 'default')
            serializer = StoreareaSerializer(storeareas, many=True)
            return Response({
                'type': type_id,
                'storeareas': serializer.data
            })
        except ValueError:
            return Response(
                {'error': 'Invalid type parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        storeareas = Storearea.objects.filter(is_active=True)
        categorized = {}
        for storearea in storeareas:
            type_key = storearea.type or 0
            if type_key not in categorized:
                categorized[type_key] = []
            serializer = SimpleStoreareaSerializer(storearea)
            categorized[type_key].append(serializer.data)

        return Response(categorized)


@api_view(['GET'])
def storearea_events(request, storearea_id):
    """
    返回指定店铺区域的所有活动ID列表
    """
    Storearea = apps.get_model('core', 'Storearea')
    EventStorearea = apps.get_model('core', 'EventStorearea')

    try:
        Storearea.objects.get(id=storearea_id, is_active=True)

        event_relations = EventStorearea.objects.filter(storearea_id=storearea_id)
        event_ids = [relation.event_id for relation in event_relations]

        return Response({
            'storearea_id': storearea_id,
            'event_ids': event_ids
        })
    except Storearea.DoesNotExist:
        return Response(
            {'error': 'Storearea not found'},
            status=status.HTTP_404_NOT_FOUND
        )


# Search活动功能

@api_view(['GET'])
def event_by_id(request, event_id):
    """
    按ID寻找活动
    """
    Event = apps.get_model('core', 'Event')
    EventSerializer = get_serializer_class('Event', 'default')

    try:
        event = Event.objects.get(id=event_id)
        serializer = EventSerializer(event)
        return Response(serializer.data)
    except Event.DoesNotExist:
        return Response(
            {'error': 'Event not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def event_search(request):
    """
    按名称寻找活动
    """
    Event = apps.get_model('core', 'Event')
    EventSerializer = get_serializer_class('Event', 'default')

    name = request.GET.get('name', '').strip()
    if not name:
        return Response(
            {'error': 'Name parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    events = Event.objects.filter(
        event_name__icontains=name,
        is_active=True
    )
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def event_list_by_type(request):
    """
    返回指定类型活动列表
    """
    Event = apps.get_model('core', 'Event')
    EventEventarea = apps.get_model('core', 'EventEventarea')
    SimpleEventSerializer = get_serializer_class('Event', 'simple')

    type_param = request.GET.get('type', '').strip()

    if type_param:
        try:
            type_id = int(type_param)
            event_ids = EventEventarea.objects.filter(
                eventarea__type=type_id
            ).values_list('event_id', flat=True).distinct()

            events = Event.objects.filter(
                id__in=event_ids,
                is_active=True
            )
            EventSerializer = get_serializer_class('Event', 'default')
            serializer = EventSerializer(events, many=True)
            return Response({
                'type': type_id,
                'events': serializer.data
            })
        except ValueError:
            return Response(
                {'error': 'Invalid type parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        events = Event.objects.filter(is_active=True)
        categorized = {}

        for event in events:
            eventarea_types = EventEventarea.objects.filter(
                event_id=event.id
            ).values_list('eventarea__type', flat=True).distinct()

            if not eventarea_types:
                type_key = 0
                if type_key not in categorized:
                    categorized[type_key] = []
                serializer = SimpleEventSerializer(event)
                categorized[type_key].append(serializer.data)
            else:
                for eventarea_type in eventarea_types:
                    type_key = eventarea_type or 0
                    if type_key not in categorized:
                        categorized[type_key] = []

                    serializer = SimpleEventSerializer(event)
                    categorized[type_key].append(serializer.data)

        return Response(categorized)


@api_view(['GET'])
def event_areas(request, event_id):
    """
    返回参加该活动的区域ID列表
    """
    Event = apps.get_model('core', 'Event')
    EventStorearea = apps.get_model('core', 'EventStorearea')
    EventEventarea = apps.get_model('core', 'EventEventarea')

    try:
        Event.objects.get(id=event_id)

        storearea_relations = EventStorearea.objects.filter(event_id=event_id)
        storearea_ids = [relation.storearea_id for relation in storearea_relations]

        eventarea_relations = EventEventarea.objects.filter(event_id=event_id)
        eventarea_ids = [relation.eventarea_id for relation in eventarea_relations]

        return Response({
            'event_id': event_id,
            'storearea_ids': storearea_ids,
            'eventarea_ids': eventarea_ids,
            'all_area_ids': storearea_ids + eventarea_ids
        })
    except Event.DoesNotExist:
        return Response(
            {'error': 'Event not found'},
            status=status.HTTP_404_NOT_FOUND
        )