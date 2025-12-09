from django.contrib.gis.geos import GEOSGeometry, Polygon
from typing import Tuple, List, Optional
from map.context import MapContext, ElementContext


# ==========================================
# Part 1: 纯几何算法 (保持不变)
# ==========================================
class GeometryAlgorithms:
    # ... (这部分代码与之前一致，省略以节省篇幅) ...
    @staticmethod
    def validate_shape_syntax(geometry: GEOSGeometry) -> Tuple[bool, str]:
        if geometry is None: return False, "Geometry is None"
        if not geometry.valid: return False, f"Invalid Geometry: {geometry.valid_reason}"
        if isinstance(geometry, Polygon) and geometry.empty: return False, "Polygon is empty"
        return True, "Valid"

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


# ==========================================
# Part 2: 业务服务 (修改部分)
# ==========================================

class MapDisplayService:
    """
    地图显示与校验服务
    """

    def __init__(self):
        self.map_ctx = MapContext()
        self.elem_ctx = ElementContext()

    def get_full_map_details(self, map_id):
        # ... (保持不变) ...
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
        # 1. 纯几何语法校验
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

        # 3. 获取所有障碍物 (修改点：在 Service 层组装数据)
        obstacles = self._collect_obstacles(map_obj, exclude_id, area_type)

        # 4. 调用算法进行物理放置校验
        return GeometryAlgorithms.check_placement(
            new_shape=geometry,
            outer_shell=outer_shell,
            holes=holes,
            existing_obstacles=obstacles
        )

    def _collect_obstacles(self, map_obj, exclude_id, exclude_type) -> List[GEOSGeometry]:
        """
        私有辅助方法：利用 MapContext 和 ElementContext 收集该地图上所有实体的形状
        """
        obstacles = []

        # 1. 从 MapContext 获取所有关联 ID
        s_ids, f_ids, o_ids, e_ids = self.map_ctx.get_map_elements(map_obj)

        # 辅助函数：处理排除逻辑
        def should_include(item_id, item_type):
            # 如果类型相同且 ID 相同，则排除（说明是正在编辑的那个对象）
            if exclude_type == item_type and str(item_id) == str(exclude_id):
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
            if should_include(e.id, 'event') and e.shape:
                obstacles.append(e.shape)

        return obstacles

    def get_map_list(self):
        """
        获取地图列表概要
        """
        # 1. 从 Context 获取所有地图
        maps = self.map_ctx.list_all_with_building()

        # 2. 初始化空属性，防止 MapSerializer 报错
        # (因为列表页通常不需要加载 heavy 的商铺/设施数据，只看底图或基础信息)
        for map_obj in maps:
            map_obj.temp_stores = []
            map_obj.temp_facilities = []
            map_obj.temp_others = []
            map_obj.temp_events = []

        return maps