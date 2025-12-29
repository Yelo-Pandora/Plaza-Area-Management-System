from django.contrib.gis.geos import Polygon, Point
from typing import Tuple, List, Optional

# 导入所有涉及的模型
from core.models import Map, Storearea, Eventarea, Otherarea, Facility, StoreareaMap, EventareaMap, OtherareaMap, \
    FacilityMap


class GuideContext:
    """
    导航模块数据上下文
    职责：只负责从数据库提取几何数据，不负责路径计算逻辑
    """

    @staticmethod
    def get_map_geometry_data(map_id: int) -> Tuple[Optional[Polygon], List[Polygon], List[Polygon]]:
        """
        一次性获取地图的边界、原始镂空以及所有障碍物

        :param map_id: 地图 ID
        :return: (outer_shell, holes, obstacles)
        """
        # 1. 获取地图底图对象
        try:
            map_obj = Map.objects.get(pk=map_id)
        except Map.DoesNotExist:
            return None, [], []

        # 2. 解析地图底图 (GeometryCollection)
        # detail[0] 通常是地板外轮廓 (Polygon)
        # detail[1:] 是地板内部的镂空 (Polygon list)
        if not map_obj.detail or len(map_obj.detail) == 0:
            return None, [], []

        outer_shell = map_obj.detail[0]
        # 确保它是 Polygon，防止脏数据
        if not isinstance(outer_shell, Polygon):
            return None, [], []

        holes = []
        # 可能有镂空，也可能没有镂空
        if len(map_obj.detail) > 1:
            holes = list(map_obj.detail[1:])

        # 3. 获取所有业务层面的障碍物
        # 将所有障碍物统一合并到一个列表中返回
        obstacles = []

        # --- A. 获取商铺区域 (Polygon) ---
        stores = Storearea.objects.filter(
            storeareamap__map_id=map_id,
            shape__isnull=False
        ).values_list('shape', flat=True)
        obstacles.extend(stores)

        # --- B. 获取活动区域 (Polygon) ---
        events = Eventarea.objects.filter(
            eventareamap__map_id=map_id,
            shape__isnull=False
        ).values_list('shape', flat=True)
        obstacles.extend(events)

        # --- C. 获取其他区域 (Polygon) ---
        others = Otherarea.objects.filter(
            otherareamap__map_id=map_id,
            shape__isnull=False
        ).values_list('shape', flat=True)
        obstacles.extend(others)

        # --- D. 获取设施 (Point -> Polygon) ---
        facilities = Facility.objects.filter(
            facilitymap__map_id=map_id,
            location__isnull=False
        ).values_list('location', flat=True)
        # 将设施点膨胀后放入障碍物列表
        for point in facilities:
            # buffer(0.5) 表示以点为中心，半径 0.5 米的圆
            if isinstance(point, Point):
                obstacles.append(point.buffer(0.5))

        return outer_shell, holes, obstacles
