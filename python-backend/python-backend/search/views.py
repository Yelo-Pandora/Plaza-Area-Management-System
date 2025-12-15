from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services import SearchService
from .serializers import (
    get_storearea_serializer, get_simple_storearea_serializer,
    get_event_serializer, get_simple_event_serializer,
    get_eventarea_serializer, get_simple_eventarea_serializer,
    get_facility_serializer, get_simple_facility_serializer,
    get_otherarea_serializer, get_simple_otherarea_serializer
)

search_service = SearchService()


# ========== 店铺搜索功能 ==========

@api_view(['GET'])
def storearea_by_id(request, storearea_id):
    """获取id为<>的商铺区域的所有信息"""
    result, error, status_code = search_service.get_storearea_by_id(storearea_id)
    if error:
        return Response(error, status=status_code)

    StoreareaSerializer = get_storearea_serializer()
    serializer = StoreareaSerializer(result)
    return Response(serializer.data)


@api_view(['GET'])
def storearea_search(request):
    """按名称寻找店铺区域"""
    name = request.GET.get('name', '').strip()
    result, error, status_code = search_service.search_storearea_by_name(name)
    if error:
        return Response(error, status=status_code)

    StoreareaSerializer = get_storearea_serializer()
    serializer = StoreareaSerializer(result, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def storearea_list_by_type(request):
    """返回指定类型店铺区域列表"""
    type_param = request.GET.get('type', '').strip()
    result, extra, error = search_service.list_storearea_by_type(type_param)
    if error:
        return Response(error, status=extra)

    if type_param:
        StoreareaSerializer = get_storearea_serializer()
        serializer = StoreareaSerializer(result, many=True)
        response_data = {'type': extra['type'], 'storeareas': serializer.data}
    else:
        categorized = {}
        SimpleStoreareaSerializer = get_simple_storearea_serializer()
        for storearea in result:
            type_key = storearea.type or 0
            if type_key not in categorized:
                categorized[type_key] = []
            serializer = SimpleStoreareaSerializer(storearea)
            categorized[type_key].append(serializer.data)
        response_data = categorized

    return Response(response_data)


@api_view(['GET'])
def storearea_events(request, storearea_id):
    """返回指定店铺区域的所有活动ID列表"""
    result, error, status_code = search_service.get_storearea_events(storearea_id)
    if error:
        return Response(error, status=status_code)
    return Response(result)


@api_view(['GET'])
def storearea_map_ids(request, storearea_id):
    """获取storearea_id为<>的活动区域所属的map_id"""
    result, error, status_code = search_service.get_storearea_map_ids(storearea_id)
    if error:
        return Response(error, status=status_code)
    return Response(result)


@api_view(['GET'])
def storearea_ids_by_map_and_type(request):
    """获取map_id为<> 且type为<>的所有storearea的id"""
    map_id = request.GET.get('map_id', '').strip()
    type_param = request.GET.get('type', '').strip()

    result, error, status_code = search_service.get_storearea_ids_by_map_and_type(map_id, type_param)
    if error:
        return Response(error, status=status_code)
    return Response(result)


@api_view(['GET'])
def all_storearea_ids_by_map(request):
    """获取map_id为<>的地图对应的所有storearea_id"""
    map_id = request.GET.get('map_id', '').strip()

    result, error, status_code = search_service.get_all_storearea_ids_by_map(map_id)
    if error:
        return Response(error, status=status_code)
    return Response(result)


# ========== 活动搜索功能 ==========

@api_view(['GET'])
def event_by_id(request, event_id):
    """按ID寻找活动"""
    result, error, status_code = search_service.get_event_by_id(event_id)
    if error:
        return Response(error, status=status_code)

    EventSerializer = get_event_serializer()
    serializer = EventSerializer(result)
    return Response(serializer.data)


@api_view(['GET'])
def event_search(request):
    """按名称寻找活动"""
    name = request.GET.get('name', '').strip()
    result, error, status_code = search_service.search_event_by_name(name)
    if error:
        return Response(error, status=status_code)

    EventSerializer = get_event_serializer()
    serializer = EventSerializer(result, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def event_list_by_type(request):
    """返回指定类型活动列表"""
    type_param = request.GET.get('type', '').strip()
    result, extra, error = search_service.list_event_by_type(type_param)
    if error:
        return Response(error, status=extra)

    if type_param:
        EventSerializer = get_event_serializer()
        serializer = EventSerializer(result, many=True)
        response_data = {'type': extra['type'], 'events': serializer.data}
    else:
        categorized = {}
        SimpleEventSerializer = get_simple_event_serializer()

        for event in result:
            # 获取该活动关联的所有Eventarea类型
            from django.apps import apps
            EventEventarea = apps.get_model('core', 'EventEventarea')
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

        response_data = categorized

    return Response(response_data)


@api_view(['GET'])
def event_areas(request, event_id):
    """返回参加该活动的区域ID列表"""
    result, error, status_code = search_service.get_event_areas(event_id)
    if error:
        return Response(error, status=status_code)
    return Response(result)


# ========== 活动区域功能 ==========

@api_view(['GET'])
def eventarea_by_id(request, eventarea_id):
    """获取id为<>的活动区域的所有信息"""
    result, error, status_code = search_service.get_eventarea_by_id(eventarea_id)
    if error:
        return Response(error, status=status_code)

    EventareaSerializer = get_eventarea_serializer()
    serializer = EventareaSerializer(result)
    return Response(serializer.data)


@api_view(['GET'])
def eventarea_ids_by_map_and_type(request):
    """获取map_id为<> 且 type为<>的所有eventarea的id"""
    map_id = request.GET.get('map_id', '').strip()
    type_param = request.GET.get('type', '').strip()

    result, error, status_code = search_service.get_eventarea_ids_by_map_and_type(map_id, type_param)
    if error:
        return Response(error, status=status_code)
    return Response(result)


@api_view(['GET'])
def eventarea_map_ids(request, eventarea_id):
    """获取eventarea_id为<>的活动区域所属的map_id"""
    result, error, status_code = search_service.get_eventarea_map_ids(eventarea_id)
    if error:
        return Response(error, status=status_code)
    return Response(result)


@api_view(['GET'])
def all_eventarea_ids_by_map(request):
    """获取map_id为<>的地图对应的所有eventarea_id"""
    map_id = request.GET.get('map_id', '').strip()

    result, error, status_code = search_service.get_all_eventarea_ids_by_map(map_id)
    if error:
        return Response(error, status=status_code)
    return Response(result)


# ========== 设施功能 ==========

@api_view(['GET'])
def facility_by_id(request, facility_id):
    """获取id为<>的设施的所有信息"""
    result, error, status_code = search_service.get_facility_by_id(facility_id)
    if error:
        return Response(error, status=status_code)

    FacilitySerializer = get_facility_serializer()
    serializer = FacilitySerializer(result)
    return Response(serializer.data)


@api_view(['GET'])
def facility_ids_by_map_and_type(request):
    """获取map_id为<> 且type为<>的所有设施id"""
    map_id = request.GET.get('map_id', '').strip()
    type_param = request.GET.get('type', '').strip()

    result, error, status_code = search_service.get_facility_ids_by_map_and_type(map_id, type_param)
    if error:
        return Response(error, status=status_code)
    return Response(result)


@api_view(['GET'])
def facility_map_ids(request, facility_id):
    """获取facility_id为<>的活动区域所属的map_id"""
    result, error, status_code = search_service.get_facility_map_ids(facility_id)
    if error:
        return Response(error, status=status_code)
    return Response(result)


@api_view(['GET'])
def all_facility_ids_by_map(request):
    """获取map_id为<>的地图对应的所有facility_id"""
    map_id = request.GET.get('map_id', '').strip()

    result, error, status_code = search_service.get_all_facility_ids_by_map(map_id)
    if error:
        return Response(error, status=status_code)
    return Response(result)


# ========== 其他区域功能 ==========

@api_view(['GET'])
def otherarea_by_id(request, otherarea_id):
    """获取id为<>的其他区域的所有信息"""
    result, error, status_code = search_service.get_otherarea_by_id(otherarea_id)
    if error:
        return Response(error, status=status_code)

    OtherareaSerializer = get_otherarea_serializer()
    serializer = OtherareaSerializer(result)
    return Response(serializer.data)


@api_view(['GET'])
def otherarea_ids_by_map_and_type(request):
    """获取map_id为<> 且type为<>的所有otherarea的id"""
    map_id = request.GET.get('map_id', '').strip()
    type_param = request.GET.get('type', '').strip()

    result, error, status_code = search_service.get_otherarea_ids_by_map_and_type(map_id, type_param)
    if error:
        return Response(error, status=status_code)
    return Response(result)


@api_view(['GET'])
def otherarea_map_ids(request, otherarea_id):
    """获取otherarea_id为<>的活动区域所属的map_id"""
    result, error, status_code = search_service.get_otherarea_map_ids(otherarea_id)
    if error:
        return Response(error, status=status_code)
    return Response(result)


@api_view(['GET'])
def all_otherarea_ids_by_map(request):
    """获取map_id为<>的地图对应的所有otherarea_id"""
    map_id = request.GET.get('map_id', '').strip()

    result, error, status_code = search_service.get_all_otherarea_ids_by_map(map_id)
    if error:
        return Response(error, status=status_code)
    return Response(result)