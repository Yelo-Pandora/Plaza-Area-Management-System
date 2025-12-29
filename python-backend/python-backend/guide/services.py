from django.contrib.gis.geos import Point, LineString, Polygon
from typing import Tuple, List, Optional
import math
import heapq

# Context 导入
from guide.context import GuideContext


class GridSystem:
    """
    辅助类：网格系统类
    负责将世界坐标(Geo)转换为离散的网格坐标(Grid)
    并管理障碍物矩阵
    """

    def __init__(self, boundary_polygon: Polygon, resolution: float = 0.5):
        """
        :param boundary_polygon: 地图的外轮廓
        :param resolution: 网格精度，例如 0.5 表示每个网格格子 0.5x0.5 米
        """
        self.resolution = resolution
        self.boundary = boundary_polygon
        # 获取多边形 boundary_polygon 的最小最大坐标
        self.min_x, self.min_y, self.max_x, self.max_y = boundary_polygon.extent
        # 计算网格系统的 x方向、 y方向各自的格子总数
        self.width = int(math.ceil((self.max_x - self.min_x) / resolution))  # 这个方法 ceil 是向上取整
        self.height = int(math.ceil((self.max_y - self.min_y) / resolution))
        # 障碍物集合，存储不可行走的网格坐标元组 (gx, gy)
        self.obstacles = set()

    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """将世界坐标转为网格坐标"""
        gx = int((x - self.min_x) / self.resolution)  # int() 是向下取整
        gy = int((y - self.min_y) / self.resolution)
        return gx, gy

    def grid_to_world(self, gx: int, gy: int) -> Tuple[float, float]:
        """将网格坐标中心转为世界坐标"""
        wx = self.min_x + (gx + 0.5) * self.resolution  # 这里是加上半格的意思，不是加上 0.5 米
        wy = self.min_y + (gy + 0.5) * self.resolution
        return wx, wy

    def mark_obstacles(self, geometry_list: List[Polygon]):
        """
        向 self.obstacles 集合中存储障碍物占据的格子坐标
        某个障碍物占据了哪些格子
        逆向思维：判断这个格子是否在这个障碍物多边形内
        """
        for poly in geometry_list:
            # 1. 性能优化：不要扫描全图，只扫描障碍物所在的那个矩形区域（Bounding Box）
            # poly.extent 返回 (min_x, min_y, max_x, max_y)
            min_x, min_y, max_x, max_y = poly.extent

            # 2. 把这个矩形区域的四个角，转换成网格坐标
            # min_gx, min_gy 是左下角格子的索引
            # max_gx, max_gy 是右上角格子的索引
            min_gx, min_gy = self.world_to_grid(min_x, min_y)
            max_gx, max_gy = self.world_to_grid(max_x, max_y)

            # 3. 修正边界，防止算出负数或者超出地图宽度的索引
            min_gx = max(0, min_gx)
            min_gy = max(0, min_gy)
            max_gx = min(self.width, max_gx + 1)  # +1 是为了保证循环能覆盖到边缘
            max_gy = min(self.height, max_gy + 1)

            # 4. 循环遍历这个小区域内的每一个格子
            for gx in range(min_gx, max_gx):
                for gy in range(min_gy, max_gy):
                    # 算出这个格子中心点在地图上的真实坐标 (wx, wy)
                    wx, wy = self.grid_to_world(gx, gy)

                    # 创建一个临时的点对象
                    cell_center = Point(wx, wy, srid=2385)

                    # 5. 关键判断：如果这个格子的中心点碰到了障碍物，这个格子就是不可走的
                    if poly.intersects(cell_center):
                        self.obstacles.add((gx, gy))

    def is_walkable(self, gx: int, gy: int) -> bool:
        """检查网格点是否在地图内且不是障碍物"""
        # 1. 数组边界检查，严格小于 self.width
        if not (0 <= gx < self.width and 0 <= gy < self.height):
            return False
        # 2. 障碍物检查
        if (gx, gy) in self.obstacles:
            return False
        # 3. 地图边界检查
        # 算出这个格子中心的真实世界坐标
        wx, wy = self.grid_to_world(gx, gy)
        # 构造一个临时的点对象
        point = Point(wx, wy, srid=2385)
        # contains() 表示如果点在多边形内部返回 True，在外部返回 False
        if not self.boundary.contains(point):
            return False

        return True


class RoutePlanService:
    """
    路径规划业务服务层
    """

    def __init__(self):
        # 创建上下文对象
        self.ctx = GuideContext()

    def validate_request_params(self, map_id, start_data, end_data) -> Tuple[bool, str]:
        """
        在View中使用的，对Request请求参数的校验逻辑
        """
        # 1. 必填项校验
        if map_id is None:
            return False, "Missing parameter: map_id"
        if not start_data or not end_data:
            return False, "Missing parameter: start or end coordinates"

        # 2. 字典结构校验
        if not isinstance(start_data, dict) or not isinstance(end_data, dict):
            return False, "Coordinates must be JSON objects with x and y"

        # 3. 坐标数值校验
        try:
            float(start_data.get('x'))
            float(start_data.get('y'))
            float(end_data.get('x'))
            float(end_data.get('y'))
        except (ValueError, TypeError):
            return False, "Coordinates x and y must be valid numbers"

        return True, "Request params are valid"

    def calculate_route(self, map_id: int, start_pt: Point, end_pt: Point) -> Optional[LineString]:
        """
        主入口：计算路径
        """
        # 1. 获取地图几何数据 (调用 Context)
        # 期望返回:
        # outer_shell: Polygon (地图地板轮廓)
        # holes: List[Polygon] (地图本身镂空)
        # obstacles: List[Geometry] (商铺、活动区、其他区域、膨胀后的设施)
        outer_shell, holes, obstacles = self.ctx.get_map_geometry_data(map_id)

        if not outer_shell:
            raise ValueError(f"Map #{map_id} outer_shell missing")

        # 2. 初始化网格系统 (Grid System)
        # 设定分辨率为 0.5 米 (可根据性能需求调整)
        grid_sys = GridSystem(outer_shell, resolution=0.5)

        # 3. 网格化障碍物
        # 将 holes 和 obstacles 合并处理
        all_obstacles = holes + obstacles
        grid_sys.mark_obstacles(all_obstacles)

        # 4. 起点、终点坐标转换
        start_node = grid_sys.world_to_grid(start_pt.x, start_pt.y)
        end_node = grid_sys.world_to_grid(end_pt.x, end_pt.y)

        # 5. 校验起终点有效性
        if not grid_sys.is_walkable(*start_node):
            raise ValueError("Start node is not walkable")
        if not grid_sys.is_walkable(*end_node):
            raise ValueError("End node is not walkable")

        # 6. 执行 A* 算法，返回网格坐标的列表
        path_nodes = self._run_astar(start_node, end_node, grid_sys)

        if not path_nodes:
            return None

        # 7. 结果转换 (Grid Nodes -> Geo LineString)
        # 将网格路径转回世界坐标的折线
        return self._construct_linestring(path_nodes, grid_sys)

    def _run_astar(self, start_node: Tuple[int, int], end_node: Tuple[int, int], grid: GridSystem) \
            -> List[Tuple[int, int]]:
        """
        A* 算法核心逻辑
        :param start_node: (gx, gy) 起点
        :param end_node: (gx, gy) 终点
        :param grid: 网格系统对象，用于判断可行走性
        :return: [(x1, y1), (x2, y2), ...] 路径列表，如果找不到路径返回 None
        """
        # 1. 初始化 open_set (优先队列)，存放 (f_score, node)，可能的扩展节点
        # f_score = g_score + h_score
        open_set = []
        heapq.heappush(open_set, (0, start_node))

        # 2. 初始化记录字典
        # came_from: 记录路径回溯，key=当前节点, value=父节点
        came_from = {}

        # g_score: 从起点到当前节点的实际代价。默认无穷大。
        g_score = {start_node: 0.0}

        # f_score: 预估总代价。默认无穷大。
        # f_score[start_node] = h(start_node, end)
        f_score = {start_node: self._heuristic(start_node, end_node)}

        # 定义移动方向和对应的代价
        # (dx, dy, cost)
        sqrt2 = math.sqrt(2)
        movements = [
            (0, 1, 1.0), (0, -1, 1.0), (1, 0, 1.0), (-1, 0, 1.0),  # 上下右左
            (1, 1, sqrt2), (1, -1, sqrt2), (-1, 1, sqrt2), (-1, -1, sqrt2)  # 对角线
        ]

        # 3. 主循环，当 open_set 非空
        while open_set:
            # 取出 f_score 最小的节点
            current_f, current = heapq.heappop(open_set)

            # --- 成功到达终点 ---
            if current == end_node:
                return self._reconstruct_path(came_from, current)

            # 遍历 8 个邻居
            for dx, dy, move_cost in movements:
                neighbor = (current[0] + dx, current[1] + dy)

                # --- 核心判断：如果邻居不可走则跳过 ---
                if not grid.is_walkable(*neighbor):
                    continue

                # 计算经过当前节点到达邻居的 tentative_g (临时G值)
                tentative_g = g_score[current] + move_cost

                # 如果临时G值小于该邻居之前的G值，或者之前没访问过该邻居 (字典里找不到 neighbor 这个 key，就返回 inf)
                if tentative_g < g_score.get(neighbor, float('inf')):
                    # 更新记录
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g

                    # 计算 f 值 = g + h
                    new_f = tentative_g + self._heuristic(neighbor, end_node)
                    f_score[neighbor] = new_f

                    # 加入优先队列等待处理
                    heapq.heappush(open_set, (new_f, neighbor))

        # 循环结束仍未找到终点
        return None

    def _reconstruct_path(self, came_from: dict, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        私有辅助方法：从终点回溯到起点，重建路径
        """
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)

        # 因为是从终点往回找的，所以要反转列表
        return total_path[::-1]

    def _heuristic(self, node_a: Tuple[int, int], node_b: Tuple[int, int]) -> float:
        """
        启发函数 (对角距离)
        """
        delta_x = abs(node_a[0] - node_b[0])
        delta_y = abs(node_a[1] - node_b[1])
        h_value = delta_x + delta_y + (math.sqrt(2) - 2) * min(delta_x, delta_y)
        return h_value

    def _construct_linestring(self, path_nodes: List[Tuple[int, int]], grid: GridSystem) -> LineString:
        """
        将网格节点序列转换为 PostGIS LineString 对象
        """
        points = []
        for gx, gy in path_nodes:
            wx, wy = grid.grid_to_world(gx, gy)
            points.append((wx, wy))

        return LineString(points, srid=2385)
