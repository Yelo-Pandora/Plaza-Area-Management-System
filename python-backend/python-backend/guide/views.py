from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.gis.geos import Point
import json

# 导入服务类
from .services import RoutePlanService


class RoutePlanView(APIView):
    """
    POST /api/guide/route/
    接收起点终点坐标，返回路径规划结果
    """
    service_class = RoutePlanService

    def post(self, request):
        service = self.service_class()

        # 读取前端传参
        # 前端传参示例: {"map_id": 1, "start": {"x": 10.0, "y": 20.0}, "end": {"x": 50.0, "y": 60.0}}
        map_id = request.data.get('map_id')
        start_data = request.data.get('start')
        end_data = request.data.get('end')

        # 这一步负责检查参数是否存在、格式是否正确、坐标是否可转换为浮点数
        is_valid, error_msg = service.validate_request_params(map_id, start_data, end_data)

        if not is_valid:
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_point = Point(float(start_data['x']), float(start_data['y']), srid=2385)
            end_point = Point(float(end_data['x']), float(end_data['y']), srid=2385)

        except Exception as e:
            # 极端异常情况
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 预期 service 返回一个 LineString 对象
            route_geometry = service.calculate_route(map_id, start_point, end_point)

            if not route_geometry:
                return Response({"error": "Route not found or unreachable"}, status=status.HTTP_404_NOT_FOUND)

            # 构造返回
            response_data = {
                # json.loads(route_geometry.geojson) 将 GeoJSON 字符串转为 Python 字典/列表
                "route": json.loads(route_geometry.geojson),
                # route_geometry.length 自动计算米制长度，然后保留 2 位小数
                "distance": round(route_geometry.length, 2)
            }

            return Response(response_data)

        except Exception as e:
            # 捕获如算法内部抛出的业务异常
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)