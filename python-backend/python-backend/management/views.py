from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import get_eventarea_serializer, get_otherarea_serializer, get_event_serializer, get_storearea_serializer
from .service import EventareaService, OtherareaService, EventService, StoreareaService


class EventareaViewSet(viewsets.ModelViewSet):
    """
    活动区域（Eventarea）的视图集
    
    注意：
    - 在management模块中处理除shape属性外的所有其他属性
    - shape属性的操作由editor模块处理
    - 不允许修改shape属性
    
    支持的操作：
    - GET /api/management/eventarea/ - 获取所有活动区域列表
    - GET /api/management/eventarea/{id}/ - 获取指定活动区域详情
    - POST /api/management/eventarea/ - 创建新的活动区域
    - PUT /api/management/eventarea/{id}/ - 完整更新活动区域（不包括shape）
    - PATCH /api/management/eventarea/{id}/ - 部分更新活动区域（不包括shape）
    - DELETE /api/management/eventarea/{id}/ - 删除指定活动区域
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
    
    def create(self, request, *args, **kwargs):
        """创建新的活动区域"""
        try:
            # 检查是否包含shape属性，如果包含则移除
            data = request.data.copy()
            if 'shape' in data:
                data.pop('shape')
            
            eventarea = EventareaService.create_eventarea(data)
            serializer = self.get_serializer(eventarea)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """完整更新活动区域（不包括shape）"""
        try:
            # 检查是否包含shape属性，如果包含则返回错误
            if 'shape' in request.data:
                return Response(
                    {'error': 'Shape attribute cannot be updated in management module'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            eventarea = EventareaService.update_eventarea(pk, request.data)
            serializer = self.get_serializer(eventarea)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, pk=None):
        """部分更新活动区域（不包括shape）"""
        try:
            # 检查是否包含shape属性，如果包含则返回错误
            if 'shape' in request.data:
                return Response(
                    {'error': 'Shape attribute cannot be updated in management module'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            eventarea = EventareaService.update_eventarea(pk, request.data)
            serializer = self.get_serializer(eventarea)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除指定活动区域"""
        try:
            EventareaService.delete_eventarea(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OtherareaViewSet(viewsets.ModelViewSet):
    """
    其他区域（Otherarea）的视图集
    
    注意：
    - 在management模块中处理除shape属性外的所有其他属性
    - shape属性的操作由editor模块处理
    - 不允许修改shape属性
    
    支持的操作：
    - GET /api/management/otherarea/ - 获取所有其他区域列表
    - GET /api/management/otherarea/{id}/ - 获取指定其他区域详情
    - POST /api/management/otherarea/ - 创建新的其他区域
    - PUT /api/management/otherarea/{id}/ - 完整更新其他区域（不包括shape）
    - PATCH /api/management/otherarea/{id}/ - 部分更新其他区域（不包括shape）
    - DELETE /api/management/otherarea/{id}/ - 删除指定其他区域
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
    
    def create(self, request, *args, **kwargs):
        """创建新的其他区域"""
        try:
            # 检查是否包含shape属性，如果包含则移除
            data = request.data.copy()
            if 'shape' in data:
                data.pop('shape')
            
            otherarea = OtherareaService.create_otherarea(data)
            serializer = self.get_serializer(otherarea)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """完整更新其他区域（不包括shape）"""
        try:
            # 检查是否包含shape属性，如果包含则返回错误
            if 'shape' in request.data:
                return Response(
                    {'error': 'Shape attribute cannot be updated in management module'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            otherarea = OtherareaService.update_otherarea(pk, request.data)
            serializer = self.get_serializer(otherarea)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, pk=None):
        """部分更新其他区域（不包括shape）"""
        try:
            # 检查是否包含shape属性，如果包含则返回错误
            if 'shape' in request.data:
                return Response(
                    {'error': 'Shape attribute cannot be updated in management module'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            otherarea = OtherareaService.update_otherarea(pk, request.data)
            serializer = self.get_serializer(otherarea)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除指定其他区域"""
        try:
            OtherareaService.delete_otherarea(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EventViewSet(viewsets.ModelViewSet):
    """
    活动（Event）的视图集
    
    支持的操作：
    - GET /api/management/event/ - 获取所有活动列表
    - GET /api/management/event/{id}/ - 获取指定活动详情
    - POST /api/management/event/ - 创建新的活动
    - PUT /api/management/event/{id}/ - 完整更新活动
    - PATCH /api/management/event/{id}/ - 部分更新活动
    - DELETE /api/management/event/{id}/ - 删除指定活动
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
    
    def create(self, request, *args, **kwargs):
        """创建新的活动"""
        try:
            event = EventService.create_event(request.data)
            serializer = self.get_serializer(event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """完整更新活动"""
        try:
            event = EventService.update_event(pk, request.data)
            serializer = self.get_serializer(event)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, pk=None):
        """部分更新活动"""
        try:
            event = EventService.update_event(pk, request.data)
            serializer = self.get_serializer(event)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除指定活动"""
        try:
            EventService.delete_event(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StoreareaViewSet(viewsets.ModelViewSet):
    """
    店铺区域（Storearea）的视图集
    
    注意：
    - 不处理shape属性，该属性由editor模块处理
    
    支持的操作：
    - GET /api/management/storearea/ - 获取所有店铺区域列表
    - GET /api/management/storearea/{id}/ - 获取指定店铺区域详情
    - POST /api/management/storearea/ - 创建新的店铺区域
    - PUT /api/management/storearea/{id}/ - 完整更新店铺区域（不包括shape）
    - PATCH /api/management/storearea/{id}/ - 部分更新店铺区域（不包括shape）
    - DELETE /api/management/storearea/{id}/ - 删除指定店铺区域
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
    
    def create(self, request, *args, **kwargs):
        """创建新的店铺区域"""
        try:
            # 检查是否包含shape属性，如果包含则移除
            data = request.data.copy()
            if 'shape' in data:
                data.pop('shape')
            
            storearea = StoreareaService.create_storearea(data)
            serializer = self.get_serializer(storearea)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        """完整更新店铺区域（不包括shape）"""
        try:
            # 检查是否包含shape属性，如果包含则返回错误
            if 'shape' in request.data:
                return Response(
                    {'error': 'Shape attribute cannot be updated in management module'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            storearea = StoreareaService.update_storearea(pk, request.data)
            serializer = self.get_serializer(storearea)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, pk=None):
        """部分更新店铺区域（不包括shape）"""
        try:
            # 检查是否包含shape属性，如果包含则返回错误
            if 'shape' in request.data:
                return Response(
                    {'error': 'Shape attribute cannot be updated in management module'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            storearea = StoreareaService.update_storearea(pk, request.data)
            serializer = self.get_serializer(storearea)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, pk=None):
        """删除指定店铺区域"""
        try:
            StoreareaService.delete_storearea(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

