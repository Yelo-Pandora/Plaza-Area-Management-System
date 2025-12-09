# import networkx as nx
# from django.contrib.gis.geos import Point, LineString
# from map.context import MapContext
# from map.services import MapServices  # 复用校验逻辑
#
#
# class GuideService:
#
#     def __init__(self, map_id: int):
#         self.map_id = map_id
#         # 通过 Context 获取数据
#         self.outer_shell, self.holes = MapContext.get_map_geometry(map_id)
#         # 获取所有障碍物 (Map镂空 + 实体店铺 + 设施)
#         # 这里的 obstacles 是纯几何对象列表
#         self.obstacles = list(self.holes) + MapContext.get_all_obstacles(map_id)
#
#     # --- 接口 5: 完善导航接口 ---
#     def find_path(self, start_point: Point, end_point: Point):
#         """
#         计算单楼层内的两点路径
#         """
#         if not self.outer_shell:
#             return {"success": False, "message": "Map not initialized"}
#
#         # 0. 校验起终点合法性 (复用 MapService 的逻辑)
#         # 注意：这里我们假设 MapService 是无状态的工具类
#         valid_start, msg_start = MapService.check_area_placement(start_point, self.map_id)
#         # 对终点的检查可能需要放宽（因为终点可能就在店铺门口），这里暂时严格检查
#         valid_end, msg_end = MapService.check_area_placement(end_point, self.map_id)
#
#         if not valid_start:
#             return {"success": False, "message": f"Start point invalid: {msg_start}"}
#         # 如果终点是店铺，check_area_placement 会报错（因为和店铺重合），
#         # 实际逻辑中应该判断终点是否在障碍物内部，如果在内部，应该“弹出”到最近的可行走点。
#         # 此处简化，假设输入点已经处理过。
#
#         # 1. 构建可见性图 (Visibility Graph)
#         graph = nx.Graph()
#
#         # 节点包括：起点、终点、所有障碍物的顶点
#         nodes = [start_point, end_point]
#         for obs in self.obstacles:
#             # 获取多边形外环坐标 (去除最后一个重复点)
#             coords = obs.exterior.coords[:-1]
#             nodes.extend([Point(c, srid=2385) for c in coords])
#
#         # 2. 构建边
#         # 优化：仅在节点数较少时使用全连接 O(N^2)
#         node_ids = range(len(nodes))
#
#         for i in node_ids:
#             graph.add_node(i, pos=(nodes[i].x, nodes[i].y))
#
#         for i in node_ids:
#             for j in range(i + 1, len(nodes)):
#                 p1 = nodes[i]
#                 p2 = nodes[j]
#
#                 if self._is_line_of_sight_clear(p1, p2):
#                     dist = p1.distance(p2)
#                     graph.add_edge(i, j, weight=dist)
#
#         # 3. 计算 Dijkstra
#         try:
#             path_indices = nx.dijkstra_path(graph, source=0, target=1)
#             path_coords = [(nodes[i].x, nodes[i].y) for i in path_indices]
#
#             return {
#                 "success": True,
#                 "distance": nx.dijkstra_path_length(graph, source=0, target=1),
#                 "path": LineString(path_coords, srid=2385),
#                 "steps": path_coords
#             }
#         except nx.NetworkXNoPath:
#             return {
#                 "success": False,
#                 "message": "No walkable path found."
#             }
#
#     def _is_line_of_sight_clear(self, p1: Point, p2: Point) -> bool:
#         """
#         私有方法：判断视线是否被阻挡
#         """
#         line = LineString(p1, p2)
#
#         # 必须在外轮廓内
#         if not self.outer_shell.contains(line):
#             return False
#
#         # 不能穿过任何障碍物
#         for obstacle in self.obstacles:
#             # 使用 relation 或者 intersection 判断
#             if obstacle.intersects(line) and not obstacle.touches(line):
#                 return False
#         return True