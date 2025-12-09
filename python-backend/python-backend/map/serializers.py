from rest_framework import serializers
from core.models import Map, Storearea, Facility, Otherarea, Eventarea
import json


# ==========================================
# 1. 子元素序列化器 (先定义，供 MapSerializer 调用)
# ==========================================

class OtherareaSerializer(serializers.ModelSerializer):
    geometry = serializers.SerializerMethodField()

    class Meta:
        model = Otherarea
        # 将 is_public 暴露出来，前端可以用不同颜色渲染
        fields = ['id', 'type', 'description', 'is_public', 'geometry']

    def get_geometry(self, obj):
        if not obj.shape: return None
        return json.loads(obj.shape.geojson)


class StoreareaSerializer(serializers.ModelSerializer):
    geometry = serializers.SerializerMethodField()

    class Meta:
        model = Storearea
        fields = ['id', 'store_name', 'type', 'logo_url', 'geometry']

    def get_geometry(self, obj):
        if not obj.shape: return None
        return json.loads(obj.shape.geojson)


class FacilitySerializer(serializers.ModelSerializer):
    geometry = serializers.SerializerMethodField()

    class Meta:
        model = Facility
        fields = ['id', 'type', 'description', 'geometry']

    def get_geometry(self, obj):
        if not obj.location: return None
        return json.loads(obj.location.geojson)


class EventareaSerializer(serializers.ModelSerializer):
    geometry = serializers.SerializerMethodField()

    class Meta:
        model = Eventarea
        fields = ['id', 'event_name', 'type', 'geometry']

    def get_geometry(self, obj):
        if not obj.shape: return None
        return json.loads(obj.shape.geojson)


# ==========================================
# 2. 地图聚合序列化器 (核心修改部分)
# ==========================================

class MapSerializer(serializers.ModelSerializer):
    """
    地图详情：包含该楼层的底图几何信息，以及关联的商铺、设施等。
    """
    building_name = serializers.CharField(source='building.name', read_only=True)
    detail_geojson = serializers.SerializerMethodField()

    # --- 关键修改开始 ---
    # 使用 source='temp_xxx' 对应 MapDisplayService 中挂载的属性名
    # read_only=True 表示这些字段只用于输出，不用于写入
    stores = StoreareaSerializer(source='temp_stores', many=True, read_only=True)
    facilities = FacilitySerializer(source='temp_facilities', many=True, read_only=True)
    other_areas = OtherareaSerializer(source='temp_others', many=True, read_only=True)
    events = EventareaSerializer(source='temp_events', many=True, read_only=True)

    # --- 关键修改结束 ---

    class Meta:
        model = Map
        fields = [
            'id',
            'building_id',
            'building_name',
            'floor_number',
            'detail_geojson',
            # 必须把新字段加入 fields 列表
            'stores',
            'facilities',
            'other_areas',
            'events'
        ]

    def get_detail_geojson(self, obj):
        """
        处理底图几何 (外轮廓 + 镂空)
        """
        if not obj.detail:
            return None

        # 保持原始坐标系 (SRID 2385)，方便前端计算米制距离
        # 如果需要经纬度，需在此处 clone().transform(4326)
        geometry = obj.detail.clone()
        return json.loads(geometry.geojson)