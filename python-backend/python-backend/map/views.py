from rest_framework import viewsets, status
from rest_framework.response import Response
from .services import MapServices
from .serializers import MapSerializer


class MapViewSet(viewsets.ViewSet):
    """
    一个简单的 ViewSet，用于列出地图信息。
    不使用 ModelViewSet 也是为了演示如何手动连接 Service 层。
    """

    # 初始化 Service
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = MapServices()

    def list(self, request):
        """
        GET /api/maps/
        返回所有地图列表
        """
        # 1. 从 Service 获取数据
        maps = self.service.get_map_list()

        # 2. 使用 Serializer 序列化数据
        serializer = MapSerializer(maps, many=True)

        # 3. 返回 HTTP 响应
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """
        GET /maps/{id}/
        获取单个地图详情
        """
        # 1. 调用 Service 获取对象
        map_obj = self.service.get_single_map(pk)

        # 2. 如果找不到，返回 404
        if map_obj is None:
            return Response(
                {"error": "Map not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 3. 序列化并返回 (注意这里 many=False，因为只是一个对象)
        serializer = MapSerializer(map_obj)
        return Response(serializer.data)