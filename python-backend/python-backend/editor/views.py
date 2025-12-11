from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.apps import apps
from django.shortcuts import get_object_or_404
from .serializers import get_storearea_serializer, get_event_serializer


class StoreareaViewSet(viewsets.ModelViewSet):
    """
    店铺区域（Storearea）的增删改查 ViewSet
    
    支持的操作：
    - GET /editor/storearea/ - 获取所有店铺列表
    - POST /editor/storearea/ - 创建新店铺
    - GET /editor/storearea/{id}/ - 获取指定店铺详情
    - PUT /editor/storearea/{id}/ - 完整更新店铺
    - PATCH /editor/storearea/{id}/ - 部分更新店铺
    - DELETE /editor/storearea/{id}/ - 删除店铺
    """
    
    def get_queryset(self):
        """获取查询集"""
        Storearea = apps.get_model('core', 'Storearea')
        return Storearea.objects.all()
    
    def get_serializer_class(self):
        """获取序列化器类"""
        return get_storearea_serializer()
    
    def list(self, request, *args, **kwargs):
        """获取所有店铺列表"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建新店铺"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        """获取指定店铺详情"""
        queryset = self.get_queryset()
        storearea = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(storearea)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """完整更新店铺"""
        queryset = self.get_queryset()
        storearea = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(storearea, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        """部分更新店铺"""
        queryset = self.get_queryset()
        storearea = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(storearea, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """删除店铺"""
        queryset = self.get_queryset()
        storearea = get_object_or_404(queryset, pk=pk)
        storearea.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """获取店铺关联的所有活动ID"""
        EventStorearea = apps.get_model('core', 'EventStorearea')
        storearea = get_object_or_404(self.get_queryset(), pk=pk)
        
        event_relations = EventStorearea.objects.filter(storearea_id=pk)
        event_ids = [relation.event_id for relation in event_relations]
        
        return Response({
            'storearea_id': pk,
            'event_ids': event_ids
        })


class EventViewSet(viewsets.ModelViewSet):
    """
    活动（Event）的增删改查 ViewSet
    
    支持的操作：
    - GET /editor/event/ - 获取所有活动列表
    - POST /editor/event/ - 创建新活动
    - GET /editor/event/{id}/ - 获取指定活动详情
    - PUT /editor/event/{id}/ - 完整更新活动
    - PATCH /editor/event/{id}/ - 部分更新活动
    - DELETE /editor/event/{id}/ - 删除活动
    """
    
    def get_queryset(self):
        """获取查询集"""
        Event = apps.get_model('core', 'Event')
        return Event.objects.all()
    
    def get_serializer_class(self):
        """获取序列化器类"""
        return get_event_serializer()
    
    def list(self, request, *args, **kwargs):
        """获取所有活动列表"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建新活动"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        """获取指定活动详情"""
        queryset = self.get_queryset()
        event = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(event)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """完整更新活动"""
        queryset = self.get_queryset()
        event = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        """部分更新活动"""
        queryset = self.get_queryset()
        event = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """删除活动"""
        queryset = self.get_queryset()
        event = get_object_or_404(queryset, pk=pk)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def areas(self, request, pk=None):
        """获取活动关联的所有区域ID（包括店铺区域和活动区域）"""
        EventStorearea = apps.get_model('core', 'EventStorearea')
        EventEventarea = apps.get_model('core', 'EventEventarea')
        event = get_object_or_404(self.get_queryset(), pk=pk)
        
        storearea_relations = EventStorearea.objects.filter(event_id=pk)
        storearea_ids = [relation.storearea_id for relation in storearea_relations]
        
        eventarea_relations = EventEventarea.objects.filter(event_id=pk)
        eventarea_ids = [relation.eventarea_id for relation in eventarea_relations]
        
        return Response({
            'event_id': pk,
            'storearea_ids': storearea_ids,
            'eventarea_ids': eventarea_ids,
            'all_area_ids': storearea_ids + eventarea_ids
        })
    
    @action(detail=True, methods=['post', 'delete'])
    def storeareas(self, request, pk=None):
        """管理活动与店铺区域的关联关系"""
        EventStorearea = apps.get_model('core', 'EventStorearea')
        event = get_object_or_404(self.get_queryset(), pk=pk)
        
        if request.method == 'POST':
            # 添加关联
            storearea_id = request.data.get('storearea_id')
            if not storearea_id:
                return Response(
                    {'error': 'storearea_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            relation, created = EventStorearea.objects.get_or_create(
                event_id=pk,
                storearea_id=storearea_id
            )
            
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
            
            deleted_count, _ = EventStorearea.objects.filter(
                event_id=pk,
                storearea_id=storearea_id
            ).delete()
            
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
    
    @action(detail=True, methods=['post', 'delete'])
    def eventareas(self, request, pk=None):
        """管理活动与活动区域的关联关系"""
        EventEventarea = apps.get_model('core', 'EventEventarea')
        event = get_object_or_404(self.get_queryset(), pk=pk)
        
        if request.method == 'POST':
            # 添加关联
            eventarea_id = request.data.get('eventarea_id')
            if not eventarea_id:
                return Response(
                    {'error': 'eventarea_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            relation, created = EventEventarea.objects.get_or_create(
                event_id=pk,
                eventarea_id=eventarea_id
            )
            
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
            
            deleted_count, _ = EventEventarea.objects.filter(
                event_id=pk,
                eventarea_id=eventarea_id
            ).delete()
            
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
