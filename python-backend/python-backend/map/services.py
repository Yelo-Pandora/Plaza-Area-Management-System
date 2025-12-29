from django.contrib.gis.geos import GEOSGeometry, Polygon
from typing import Tuple, List
from map.context import MapContext, ElementContext
import json
from django.contrib.gis.geos import GEOSGeometry


"""
Part 1: 纯几何算法
"""

class GeometryAlgorithms:
    @staticmethod
    def validate_shape_syntax(geometry: GEOSGeometry) -> Tuple[bool, str]:
        if geometry is None: return False, "Geometry is None"
        if not geometry.valid: return False, f"Invalid Geometry: {geometry.valid_reason}"
        if isinstance(geometry, Polygon) and geometry.empty: return False, "Polygon is empty"
        return True, "Valid"

    @staticmethod
    def get_distance_between_areas(shape1: GEOSGeometry, shape2: GEOSGeometry) -> float:
        """
        接口 3: 获取输入的两个区域之间的距离
        """
        if not shape1 or not shape2:
            return -1.0
        # distance() 计算的是两个几何体之间最近点的欧几里得距离
        # 单位取决于 SRID (2385 为米)
        return shape1.distance(shape2)

    @staticmethod
    def validate_holes_inside_shell(outer_shell: GEOSGeometry, holes: List[GEOSGeometry]) -> Tuple[bool, str]:
        """
        接口 2: 镂空本身有无超出外轮廓区域
        """
        if not outer_shell:
            return False, "Outer shell is missing"

        if not holes:
            return True, "No holes to validate"

        for i, hole in enumerate(holes, start=1):
            # hole 必须完全在 outer_shell 内部 (contains)
            # 任何一部分超出或仅仅是相交都算非法
            if not outer_shell.contains(hole):
                return False, f"Hole #{i} is outside or intersecting the map boundary."

        return True, "All holes are valid"

    @staticmethod
    def check_placement(new_shape, outer_shell, holes, existing_obstacles):
        if not outer_shell: return False, "Map shell missing"
        if not outer_shell.contains(new_shape): return False, "Area exceeds map outer boundary"
        for i, hole in enumerate(holes):
            if hole.intersects(new_shape): return False, f"Area intersects with map hole #{i + 1}"
        for existing_shape in existing_obstacles:
            if existing_shape and existing_shape.intersects(new_shape):
                return False, "Area overlaps with an existing area"
        return True, "Placement valid"


"""
Part 2: 业务服务 (修改部分)
"""

class MapDisplayService:
    """
    地图显示与校验服务
    """

    def __init__(self):
        self.map_ctx = MapContext()
        self.elem_ctx = ElementContext()

    def get_full_map_details(self, map_id):
        map_obj = self.map_ctx.get_map_with_building(map_id)
        if not map_obj: return None

        s_ids, f_ids, o_ids, e_ids = self.map_ctx.get_map_elements(map_obj)

        map_obj.temp_stores = self.elem_ctx.get_stores_by_ids(s_ids)
        map_obj.temp_facilities = self.elem_ctx.get_facilities_by_ids(f_ids)
        map_obj.temp_others = self.elem_ctx.get_others_by_ids(o_ids)
        map_obj.temp_events = self.elem_ctx.get_events_by_ids(e_ids)

        return map_obj

    def validate_geometry(self, geometry, map_id, exclude_id=None, area_type=None):
        """
        几何校验业务流程
        """
        # 1. 几何语法校验
        is_valid, msg = GeometryAlgorithms.validate_shape_syntax(geometry)
        if not is_valid:
            return False, msg

        # 2. 获取地图数据
        map_obj = self.map_ctx.get_map_with_building(map_id)
        if not map_obj or not map_obj.detail:
            return False, "Map data not found or empty"

        # 解析外轮廓和镂空
        outer_shell = map_obj.detail[0]
        holes = list(map_obj.detail[1:]) if len(map_obj.detail) > 1 else []

        # 3. 获取所有障碍物
        obstacles = self._collect_obstacles(map_obj, exclude_id, area_type)

        # 4. 调用算法进行物理放置校验
        return GeometryAlgorithms.check_placement(
            new_shape=geometry,
            outer_shell=outer_shell,
            holes=holes,
            existing_obstacles=obstacles
        )

    def _collect_obstacles(self, map_obj, exclude_id, area_type) -> List[GEOSGeometry]:
        """
        私有辅助方法：利用 MapContext 和 ElementContext 收集该地图上所有实体的形状
        """
        obstacles = []

        # 1. 从 MapContext 获取所有关联 ID
        s_ids, f_ids, o_ids, e_ids = self.map_ctx.get_map_elements(map_obj)

        # 辅助函数：处理排除逻辑
        def should_include(item_id, item_type):
            # 如果类型相同且 ID 相同，则排除
            if area_type == item_type and str(item_id) == str(exclude_id):
                return False
            return True

        # 2. 从 ElementContext 获取对象并提取形状

        # A. 商铺 (Stores)
        stores = self.elem_ctx.get_stores_by_ids(s_ids)
        for s in stores:
            if should_include(s.id, 'store') and s.shape:
                obstacles.append(s.shape)

        # B. 设施 (Facilities) - 需要 Buffer 处理
        facilities = self.elem_ctx.get_facilities_by_ids(f_ids)
        for f in facilities:
            if should_include(f.id, 'facility') and f.location:
                # 设施通常是点，必须膨胀成多边形才能进行碰撞检测
                # 假设半径 0.5 米
                obstacles.append(f.location.buffer(0.5))

        # C. 其他区域 (Otherareas)
        others = self.elem_ctx.get_others_by_ids(o_ids)
        for o in others:
            if should_include(o.id, 'other') and o.shape:
                obstacles.append(o.shape)

        # D. 活动区域 (Events)
        events = self.elem_ctx.get_events_by_ids(e_ids)
        for e in events:
            if should_include(e.id, 'event') and e.shape and e.is_active:
                obstacles.append(e.shape)

        return obstacles

    def get_map_list(self):
        """
        获取地图列表概要
        """
        # 1. 从 Context 获取所有地图
        maps = self.map_ctx.list_all_with_building()

        # 2. 初始化空属性，防止 MapSerializer 报错
        for map_obj in maps:
            map_obj.temp_stores = []
            map_obj.temp_facilities = []
            map_obj.temp_others = []
            map_obj.temp_events = []

        return maps

    def validate_batch(self, map_id, updates_list):
        """
        批量校验
        :param map_id: 地图ID
        :param updates_list: 预处理过的列表，每项包含 'geos_obj' (GEOSGeometry)
        :return: (is_valid, errors_list)
        """
        # 1. 获取地图底图 (外框和镂空)
        map_obj = self.map_ctx.get_map_with_building(map_id)
        if not map_obj or not map_obj.detail:
            return False, ["地图数据缺失"]

        outer_shell = map_obj.detail[0]
        holes = list(map_obj.detail[1:]) if len(map_obj.detail) > 1 else []

        # 2. 整理新数据 (不再需要解析 JSON，直接取对象)
        new_geometries = []
        updated_keys = set()

        for item in updates_list:
            # 直接获取 View 层解析好的几何对象
            shape = item['geos_obj']

            # 统一为多边形用于碰撞检测 (点 -> 圆)
            collision_shape = shape.buffer(0.3) if shape.geom_type == 'Point' else shape

            item_type = str(item.get('type')).lower()
            item_id = str(item.get('id'))

            new_geometries.append({
                'id': item_id,
                'type': item_type,
                'shape': collision_shape,
                'name': item.get('name', 'Unknown')
            })

            key = f"{item_type}-{item_id}"
            updated_keys.add(key)

        # 3. 从数据库获取“背景障碍物” (排除掉在 updated_keys 里的项)
        s_ids, f_ids, o_ids, e_ids = self.map_ctx.get_map_elements(map_obj)
        static_obstacles = []

        def add_static(objects, type_name):
            for obj in objects:
                key = f"{type_name}-{str(obj.id)}"
                if key not in updated_keys:
                    shape = getattr(obj, 'shape', None)
                    if type_name == 'facility':
                        loc = getattr(obj, 'location', None)
                        if loc: shape = loc.buffer(0.3)

                    if shape:
                        static_obstacles.append(shape)

        add_static(self.elem_ctx.get_stores_by_ids(s_ids), 'store')
        add_static(self.elem_ctx.get_facilities_by_ids(f_ids), 'facility')
        add_static(self.elem_ctx.get_others_by_ids(o_ids), 'other')
        active_events = [e for e in self.elem_ctx.get_events_by_ids(e_ids) if e.is_active]
        add_static(active_events, 'event')

        # 4. 执行校验
        errors = []

        for curr in new_geometries:
            curr_shape = curr['shape']

            # 4.1 边界检查
            if not outer_shell.contains(curr_shape):
                errors.append(f"[{curr['name']}] 超出地图边界")
                continue

            for hole in holes:
                if hole.intersects(curr_shape) and not hole.touches(curr_shape):
                    errors.append(f"[{curr['name']}] 进入了地图镂空/中庭区域")
                    break

            # 4.2 静态障碍物碰撞
            for obs in static_obstacles:
                if obs.intersects(curr_shape) and not obs.touches(curr_shape):
                    errors.append(f"[{curr['name']}] 与未修改的固定区域重叠")
                    break

            # 4.3 动态物体互撞 (A 撞 B)
            for other in new_geometries:
                if curr['id'] == other['id'] and curr['type'] == other['type']:
                    continue

                if curr['type'] == 'facility' and other['type'] == 'facility':
                    continue

                if other['shape'].intersects(curr_shape) and not other['shape'].touches(curr_shape):
                    if curr['id'] < other['id']:
                        errors.append(f"[{curr['name']}] 与 [{other['name']}] 重叠")
                    break

        if len(errors) > 0:
            return False, errors

        return True, []