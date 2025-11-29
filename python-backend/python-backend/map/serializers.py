from rest_framework import serializers
from .context import Map
import json


class MapSerializer(serializers.ModelSerializer):
    # 将 building 转换为字符串名称，或者你可以嵌套另一个 Serializer
    building_name = serializers.CharField(source='building.name', read_only=True)

    # 自定义字段处理 detail (GeometryCollection)
    detail_geojson = serializers.SerializerMethodField()

    class Meta:
        model = Map
        fields = ['id', 'building_id', 'building_name', 'floor_number', 'detail_geojson']

    def get_detail_geojson(self, obj):
        """
        将 GeometryCollection 处理为前端可用的 GeoJSON。
        同时将坐标系从 SRID 2385 (TWD97) 转换为 SRID 4326 (WGS84 经纬度)。
        """
        if not obj.detail:
            return None

        # 1. 克隆几何对象以避免修改数据库实例
        geometry = obj.detail.clone()
        # geometry.transform(4326)

        # 3. 返回 GeoJSON 字典对象 (而不是字符串，这样 DRF 会将其作为 JSON 对象输出)
        return json.loads(geometry.geojson)