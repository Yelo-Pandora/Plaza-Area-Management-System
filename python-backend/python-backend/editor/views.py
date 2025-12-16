from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import get_storearea_serializer, get_event_serializer, get_eventarea_serializer, get_otherarea_serializer
from .service import StoreareaService, EventService, EventareaService, OtherareaService


class StoreareaViewSet(viewsets.ModelViewSet):
    """
    店铺区域（Storearea）的视图集
    
    注意：在editor模块中只处理shape属性的更新，其他属性在management中实现
    
    支持的操作：
    - GET /api/editor/storearea/ - 获取所有店铺区域列表
    - GET /api/editor/storearea/{id}/ - 获取指定店铺区域详情
    - POST /api/editor/storearea/ - 创建店铺区域（仅支持shape属性）
    - PATCH /api/editor/storearea/{id}/ - 部分更新店铺区域（仅支持shape属性）
    - DELETE /api/editor/storearea/{id}/ - 删除店铺区域
    """
    
    def get_serializer_class(self):
        """获取序列化器类"""
        return get_storearea_serializer()
    
    def get_queryset(self):
        """获取所有店铺区域"""
        return StoreareaService.get_all_storeareas()
    
    def list(self, request, *args, **kwargs):
        """获取所有店铺区域列表"""
        storeareas = StoreareaService.get_all_storeareas()
        serializer = self.get_serializer(storeareas, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """获取指定店铺区域详情"""
        storearea = get_object_or_404(StoreareaService.get_all_storeareas(), pk=pk)
        serializer = self.get_serializer(storearea)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """不允许完整更新店铺区域"""
        return Response(
            {'error': 'Full update not allowed in editor module'}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, pk=None):
        """部分更新店铺区域（仅支持shape属性）"""
        if 'shape' not in request.data:
            return Response(
                {'error': 'Only shape attribute can be updated in editor module'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        storearea = get_object_or_404(StoreareaService.get_all_storeareas(), pk=pk)
        shape = request.data.get('shape')
        
        updated_storearea = StoreareaService.update_shape(pk, shape)
        serializer = self.get_serializer(updated_storearea)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建店铺区域（仅支持shape属性）"""
        if 'shape' not in request.data:
            return Response(
                {'error': 'Only shape attribute can be provided when creating storearea in editor module'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        shape = request.data.get('shape')
        new_storearea = StoreareaService.create_storearea(shape)
        serializer = self.get_serializer(new_storearea)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, pk=None):
        """删除店铺区域"""
        StoreareaService.delete_storearea(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """获取店铺关联的所有活动ID"""
        event_ids = StoreareaService.get_events_for_storearea(pk)
        return Response({
            'storearea_id': pk,
            'event_ids': event_ids
        })


class EventViewSet(viewsets.ModelViewSet):
    """
    活动（Event）的视图集
    
    注意：Event模型没有shape字段，因此不支持shape属性更新

    支持的操作：
    - GET /api/editor/event/ - 获取所有活动列表
    - GET /api/editor/event/{id}/ - 获取指定活动详情
    - GET /api/editor/event/{id}/areas/ - 获取活动关联的所有区域ID
    - POST/DELETE /api/editor/event/{id}/storeareas/ - 管理活动与店铺区域的关联关系
    """
    
    def get_serializer_class(self):
        """获取序列化器类"""
        return get_event_serializer()
    
    def get_queryset(self):
        """获取所有活动"""
        return EventService.get_all_events()
    
    def list(self, request, *args, **kwargs):
        """获取所有活动列表"""
        events = EventService.get_all_events()
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """获取指定活动详情"""
        event = get_object_or_404(EventService.get_all_events(), pk=pk)
        serializer = self.get_serializer(event)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """不允许完整更新活动"""
        return Response(
            {'error': 'Full update not allowed in editor module'}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, pk=None):
        """不允许在editor模块中更新活动"""
        return Response(
            {'error': 'Update not allowed in editor module'}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def create(self, request, *args, **kwargs):
        """不允许在editor模块中创建活动"""
        return Response(
            {'error': 'Create not allowed in editor module'}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, pk=None):
        """不允许在editor模块中删除活动"""
        return Response(
            {'error': 'Delete not allowed in editor module'}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    @action(detail=True, methods=['get'])
    def areas(self, request, pk=None):
        """获取活动关联的所有区域ID（包括店铺区域和活动区域）"""
        areas = EventService.get_areas_for_event(pk)
        return Response({
            'event_id': pk,
            'storearea_ids': areas['storearea_ids'],
            'eventarea_ids': areas['eventarea_ids'],
            'all_area_ids': areas['all_area_ids']
        })
    
    @action(detail=True, methods=['post', 'delete'])
    def storeareas(self, request, pk=None):
        """管理活动与店铺区域的关联关系"""
        if request.method == 'POST':
            # 添加关联
            storearea_id = request.data.get('storearea_id')
            if not storearea_id:
                return Response(
                    {'error': 'storearea_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            relation, created = EventService.add_storearea_to_event(pk, storearea_id)
            
            if created:
                return Response(
                    {'message': 'Relation created successfully'},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'message': 'Relation already exists'},
                    status=status.HTTP_200_OK
                )
        
        elif request.method == 'DELETE':
            # 删除关联
            storearea_id = request.data.get('storearea_id')
            if not storearea_id:
                return Response(
                    {'error': 'storearea_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            deleted_count, _ = EventService.remove_storearea_from_event(pk, storearea_id)
            
            if deleted_count > 0:
                return Response(
                    {'message': 'Relation deleted successfully'},
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {'error': 'Relation not found'},
                    status=status.HTTP_404_NOT_FOUND
                )


class EventareaViewSet(viewsets.ModelViewSet):
    """
    活动区域（Eventarea）的视图集
    
    注意：在editor模块中只处理shape属性的更新，其他属性在management中实现
    
    支持的操作：
    - GET /api/editor/eventarea/ - 获取所有活动区域列表
    - GET /api/editor/eventarea/{id}/ - 获取指定活动区域详情
    - POST /api/editor/eventarea/ - 创建活动区域（仅支持shape属性）
    - PATCH /api/editor/eventarea/{id}/ - 部分更新活动区域（仅支持shape属性）
    - DELETE /api/editor/eventarea/{id}/ - 删除活动区域
    """
    
    def get_serializer_class(self):
        """获取序列化器类"""
        return get_eventarea_serializer()
    
    def get_queryset(self):
        """获取所有活动区域"""
        return EventareaService.get_all_eventareas()
    
    def list(self, request, *args, **kwargs):
        """获取所有活动区域列表"""
        eventareas = EventareaService.get_all_eventareas()
        serializer = self.get_serializer(eventareas, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """获取指定活动区域详情"""
        eventarea = get_object_or_404(EventareaService.get_all_eventareas(), pk=pk)
        serializer = self.get_serializer(eventarea)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """不允许完整更新活动区域"""
        return Response(
            {'error': 'Full update not allowed in editor module'}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, pk=None):
        """部分更新活动区域（仅支持shape属性）"""
        if 'shape' not in request.data:
            return Response(
                {'error': 'Only shape attribute can be updated in editor module'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        eventarea = get_object_or_404(EventareaService.get_all_eventareas(), pk=pk)
        shape = request.data.get('shape')
        
        updated_eventarea = EventareaService.update_eventarea_shape(pk, shape)
        serializer = self.get_serializer(updated_eventarea)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建活动区域（仅支持shape属性）"""
        if 'shape' not in request.data:
            return Response(
                {'error': 'Only shape attribute can be provided when creating eventarea in editor module'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        shape = request.data.get('shape')
        new_eventarea = EventareaService.create_eventarea(shape)
        serializer = self.get_serializer(new_eventarea)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, pk=None):
        """删除活动区域"""
        EventareaService.delete_eventarea(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OtherareaViewSet(viewsets.ModelViewSet):
    """
    其他区域（Otherarea）的视图集
    
    注意：在editor模块中只处理shape属性的更新，其他属性在management中实现
    
    支持的操作：
    - GET /api/editor/otherarea/ - 获取所有其他区域列表
    - GET /api/editor/otherarea/{id}/ - 获取指定其他区域详情
    - POST /api/editor/otherarea/ - 创建其他区域（仅支持shape属性）
    - PATCH /api/editor/otherarea/{id}/ - 部分更新其他区域（仅支持shape属性）
    - DELETE /api/editor/otherarea/{id}/ - 删除其他区域
    """
    
    def get_serializer_class(self):
        """获取序列化器类"""
        return get_otherarea_serializer()
    
    def get_queryset(self):
        """获取所有其他区域"""
        return OtherareaService.get_all_otherareas()
    
    def list(self, request, *args, **kwargs):
        """获取所有其他区域列表"""
        otherareas = OtherareaService.get_all_otherareas()
        serializer = self.get_serializer(otherareas, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """获取指定其他区域详情"""
        otherarea = get_object_or_404(OtherareaService.get_all_otherareas(), pk=pk)
        serializer = self.get_serializer(otherarea)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """不允许完整更新其他区域"""
        return Response(
            {'error': 'Full update not allowed in editor module'}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, pk=None):
        """部分更新其他区域（仅支持shape属性）"""
        if 'shape' not in request.data:
            return Response(
                {'error': 'Only shape attribute can be updated in editor module'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        otherarea = get_object_or_404(OtherareaService.get_all_otherareas(), pk=pk)
        shape = request.data.get('shape')
        
        updated_otherarea = OtherareaService.update_otherarea_shape(pk, shape)
        serializer = self.get_serializer(updated_otherarea)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建其他区域（仅支持shape属性）"""
        if 'shape' not in request.data:
            return Response(
                {'error': 'Only shape attribute can be provided when creating otherarea in editor module'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        shape = request.data.get('shape')
        new_otherarea = OtherareaService.create_otherarea(shape)
        serializer = self.get_serializer(new_otherarea)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, pk=None):
        """删除其他区域"""
        OtherareaService.delete_otherarea(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post', 'delete'])
    def eventareas(self, request, pk=None):
        """管理活动与活动区域的关联关系"""
        if request.method == 'POST':
            # 添加关联
            eventarea_id = request.data.get('eventarea_id')
            if not eventarea_id:
                return Response(
                    {'error': 'eventarea_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            relation, created = EventService.add_eventarea_to_event(pk, eventarea_id)
            
            if created:
                return Response(
                    {'message': 'Relation created successfully'},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'message': 'Relation already exists'},
                    status=status.HTTP_200_OK
                )
        
        elif request.method == 'DELETE':
            # 删除关联
            eventarea_id = request.data.get('eventarea_id')
            if not eventarea_id:
                return Response(
                    {'error': 'eventarea_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            deleted_count, _ = EventService.remove_eventarea_from_event(pk, eventarea_id)
            
            if deleted_count > 0:
                return Response(
                    {'message': 'Relation deleted successfully'},
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {'error': 'Relation not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
