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


class MapBatchValidationView(APIView):
    """POST /api/maps/validate_batch/ (批量校验)"""
    service_class = MapDisplayService

    def post(self, request):
        service = self.service_class()

        map_id = request.data.get('map_id')
        updates = request.data.get('updates', [])

        if not map_id:
            return Response({"error": "map_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 数据预处理：在 View 层统一解析几何并修正 SRID
        processed_updates = []
        for i, item in enumerate(updates):
            try:
                # 1. 提取原始数据
                raw_geo = item.get('geometry') or item.get('location')
                if not raw_geo: continue

                # 2. 转字符串
                shape_str = json.dumps(raw_geo) if isinstance(raw_geo, dict) else raw_geo

                # 3. 解析几何
                shape = GEOSGeometry(shape_str)

                # 4. 强制修正 SRID (与 MapValidationView 保持一致)
                if shape.srid != 2385:
                    shape.srid = 2385

                # 5. 将处理好的 GEOSGeometry 对象注入 item
                item['geos_obj'] = shape
                processed_updates.append(item)

            except Exception as e:
                # 如果解析失败，直接返回 400，中断处理
                return Response(
                    {"error": f"Invalid geometry at index {i} (ID: {item.get('id')}): {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 调用 Service，传入包含 GEOSGeometry 对象的列表
        is_valid, errors = service.validate_batch(map_id, processed_updates)

        return Response({
            "valid": is_valid,
            "errors": errors
        })