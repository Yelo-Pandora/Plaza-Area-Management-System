from rest_framework import serializers
from core.models import Map, Storearea, Facility, Otherarea, Eventarea
import json

"""
子元素序列化器 (供 MapSerializer 调用)
"""

class OtherareaSerializer(serializers.ModelSerializer):
    geometry = serializers.SerializerMethodField()

    class Meta:
        model = Otherarea
        # 将 is_public 暴露出来，前端可以用不同颜色渲染
        fields = ['id', 'type', 'description', 'is_public',  'is_active', 'geometry']

    @staticmethod
    def get_geometry(obj):
        if not obj.shape: return None
        return json.loads(obj.shape.geojson)


class StoreareaSerializer(serializers.ModelSerializer):
    geometry = serializers.SerializerMethodField()

    class Meta:
        model = Storearea
        fields = ['id', 'store_name', 'type', 'logo_url', 'is_active', 'geometry']

    @staticmethod
    def get_geometry(obj):
        if not obj.shape: return None
        return json.loads(obj.shape.geojson)


class FacilitySerializer(serializers.ModelSerializer):
    geometry = serializers.SerializerMethodField()

    class Meta:
        model = Facility
        fields = ['id', 'type', 'description', 'is_active', 'geometry']

    @staticmethod
    def get_geometry(obj):
        if not obj.location: return None
        return json.loads(obj.location.geojson)


class EventareaSerializer(serializers.ModelSerializer):
    geometry = serializers.SerializerMethodField()

    class Meta:
        model = Eventarea
        fields = ['id', 'description',  'type', 'is_active', 'geometry']

    @staticmethod
    def get_geometry(obj):
        if not obj.shape: return None
        return json.loads(obj.shape.geojson)


"""
地图聚合序列化器 (核心修改部分)
"""

class MapSerializer(serializers.ModelSerializer):
    """
    地图详情：包含该楼层的底图几何信息，以及关联的商铺、设施等。
    """
    building_name = serializers.CharField(source='building.name', read_only=True)
    detail_geojson = serializers.SerializerMethodField()

    # 对应 MapDisplayService 中挂载的属性名
    # 这些字段只用于输出，不用于写入
    stores = StoreareaSerializer(source='temp_stores', many=True, read_only=True)
    facilities = FacilitySerializer(source='temp_facilities', many=True, read_only=True)
    other_areas = OtherareaSerializer(source='temp_others', many=True, read_only=True)
    events = EventareaSerializer(source='temp_events', many=True, read_only=True)


    class Meta:
        model = Map
        fields = [
            'id',
            'building_id',
            'building_name',
            'floor_number',
            'detail_geojson',
            'stores',
            'facilities',
            'other_areas',
            'events'
        ]

    @staticmethod
    def get_detail_geojson(obj):
        """
        处理底图几何 (外轮廓 + 镂空)
        """
        if not obj.detail:
            return None

        # 保持原始坐标系 (SRID 2385)，方便前端计算米制距离
        geometry = obj.detail.clone()
        return json.loads(geometry.geojson)