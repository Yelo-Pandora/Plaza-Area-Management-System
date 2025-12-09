from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.gis.geos import GEOSGeometry
import json

from .serializers import MapSerializer  # 序列化器依然需要，用于格式化输出
from map.services import MapDisplayService


class MapViewSet(viewsets.ViewSet):
    """
    只读 ViewSet，不继承 ModelViewSet
    """
    service_class = MapDisplayService

    def list(self, request):
        """GET /api/maps/"""
        service = self.service_class()

        # 1. 调用 Service 获取列表
        maps = service.get_map_list()

        # 2. 序列化返回
        # 注意：这里会返回所有地图的 GeoJSON，数据量可能较大
        # 实际生产中建议单独定义一个 SimpleMapSerializer (不含 detail_geojson) 用于列表
        serializer = MapSerializer(maps, many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """GET /api/maps/{id}/"""
        service = self.service_class()

        # 1. 调用 Service 获取组装好的对象
        map_data = service.get_full_map_details(pk)

        if not map_data:
            return Response({"error": "Map not found"}, status=status.HTTP_404_NOT_FOUND)

        # 2. 使用 Serializer 格式化 Service 返回的数据
        # 注意：Serializer 内部字段 source='temp_stores' 需要对应 Service 挂载的属性
        serializer = MapSerializer(map_data)
        return Response(serializer.data)


class MapValidationView(APIView):
    """POST /api/maps/validate/"""
    service_class = MapDisplayService

    def post(self, request):
        service = self.service_class()

        # 1. 参数提取
        geometry_data = request.data.get('geometry')
        map_id = request.data.get('map_id')
        area_type = request.data.get('type')
        exclude_id = request.data.get('exclude_id')

        # 2. 数据预处理
        try:
            shape_str = json.dumps(geometry_data) if isinstance(geometry_data, dict) else geometry_data
            shape = GEOSGeometry(shape_str)
            if shape.srid != 2385: shape.srid = 2385
        except Exception:
            return Response({"error": "Invalid Geometry"}, status=400)

        # 3. 调用 Service 业务逻辑
        is_valid, reason = service.validate_geometry(shape, map_id, exclude_id, area_type)

        return Response({"valid": is_valid, "reason": reason})