from django.test import TestCase
from unittest.mock import MagicMock, patch
from django.contrib.gis.geos import Polygon, Point, LineString
from guide.services import RoutePlanService, GridSystem
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.gis.geos import Polygon, GeometryCollection, Point
from core.models import Map, Building, Storearea, StoreareaMap


class GridSystemTestCase(TestCase):
    """
    测试 GridSystem 类的底层逻辑 (坐标转换、障碍物标记、边界检查)
    """

    def setUp(self):
        # 创建一个 10x10 的正方形地图 (SRID=2385)
        # 坐标范围: (0,0) -> (10,10)
        self.boundary = Polygon(((0, 0), (0, 10), (10, 10), (10, 0), (0, 0)), srid=2385)
        # 分辨率设为 1.0 米，方便计算 (网格大小 10x10)
        self.grid = GridSystem(self.boundary, resolution=1.0)

    def test_coordinate_conversion(self):
        """测试世界坐标与网格坐标的相互转换"""
        # 测试 world_to_grid (向下取整)
        # 坐标 (1.5, 1.5) 应该落在 (1, 1) 格子
        gx, gy = self.grid.world_to_grid(1.5, 1.5)
        self.assertEqual((gx, gy), (1, 1))

        # 测试 grid_to_world (取中心点)
        # 格子 (1, 1) 的中心应该是 (1.5, 1.5)
        wx, wy = self.grid.grid_to_world(1, 1)
        self.assertEqual((wx, wy), (1.5, 1.5))

    def test_mark_obstacles(self):
        """测试障碍物栅格化逻辑"""
        # 创建一个位于地图中心的障碍物 (4,4) 到 (6,6)
        obstacle = Polygon(((4, 4), (4, 6), (6, 6), (6, 4), (4, 4)), srid=2385)

        self.grid.mark_obstacles([obstacle])

        # 检查障碍物内部的点 (5, 5) -> 不可走
        self.assertFalse(self.grid.is_walkable(5, 5))

        # 检查障碍物边缘的点 (网格化后可能会占据边缘)
        # (4, 4) 根据 intersects 判定通常会被占据
        self.assertFalse(self.grid.is_walkable(4, 4))

        # 检查开阔区域的点 (1, 1) -> 可走
        self.assertTrue(self.grid.is_walkable(1, 1))

    def test_boundary_check_complex_shape(self):
        """
        测试不规则形状地图的边界检查 (L型地图)
        验证 is_walkable 中的 boundary.contains 逻辑
        """
        # 创建一个 L 型多边形 (缺口在右上角)
        # (0,0) -> (0,10) -> (5,10) -> (5,5) -> (10,5) -> (10,0) -> (0,0)
        l_shape_wkt = "POLYGON((0 0, 0 10, 5 10, 5 5, 10 5, 10 0, 0 0))"
        l_shape = Polygon.from_ewkt(l_shape_wkt)
        l_shape.srid = 2385

        grid = GridSystem(l_shape, resolution=1.0)

        # 1. 测试在地图内的点 (2, 2)
        self.assertTrue(grid.is_walkable(2, 2))

        # 2. 测试在 L 型缺口处的点 (8, 8)
        # 虽然 (8, 8) 在 GridSystem 的数组索引范围内 (width=10, height=10)
        # 但它在物理上位于大楼外部
        self.assertFalse(grid.is_walkable(8, 8))


class RoutePlanServiceTestCase(TestCase):
    """
    测试 A* 算法服务层逻辑
    使用 Mock 屏蔽 Context/数据库 操作
    """

    def setUp(self):
        self.service = RoutePlanService()
        # 基础地图: 20x20 米的正方形
        self.map_boundary = Polygon(((0, 0), (0, 20), (20, 20), (20, 0), (0, 0)), srid=2385)

    @patch('guide.services.GuideContext')
    def test_simple_straight_path(self, MockContext):
        """测试无障碍物的直线路径"""
        # --- Mock 设置 ---
        mock_ctx_instance = MockContext.return_value
        # 返回: (外框, 镂空[], 障碍物[])
        mock_ctx_instance.get_map_geometry_data.return_value = (self.map_boundary, [], [])

        # 替换 service 中的 ctx
        self.service.ctx = mock_ctx_instance

        # --- 执行测试 ---
        start = Point(2, 2, srid=2385)
        end = Point(18, 18, srid=2385)

        # 运行算法
        route = self.service.calculate_route(map_id=1, start_pt=start, end_pt=end)

        # --- 断言 ---
        self.assertIsInstance(route, LineString)
        # 直线距离约为 22.62 米
        # A* 也是走的对角线，长度应该非常接近直线距离
        self.assertAlmostEqual(route.length, start.distance(end), delta=1.0)

    @patch('guide.services.GuideContext')
    def test_obstacle_avoidance(self, MockContext):
        """测试绕行逻辑：起点和终点中间有一堵墙，必须从缺口绕过去"""
        # --- Mock 设置 ---
        mock_ctx_instance = MockContext.return_value

        # 定义障碍物：一堵带缺口的墙
        # 墙的范围：y轴 9到11，x轴 5到20。
        # 这意味着 x轴 0到5 的区域是空的（缺口），路径只能从这里通过。
        wall_with_gap = Polygon(((5, 9), (5, 11), (20, 11), (20, 9), (5, 9)), srid=2385)

        # 模拟 Context 返回：地图边界、无镂空、以及上面定义的障碍物
        mock_ctx_instance.get_map_geometry_data.return_value = (
            self.map_boundary,
            [],
            [wall_with_gap]
        )
        self.service.ctx = mock_ctx_instance

        # --- 执行测试 ---
        # 起点(10, 2) -> 终点(10, 18)
        # 直线连线会被墙挡住 (墙在 y=9~11, x=5~20)
        start = Point(10, 2, srid=2385)
        end = Point(10, 18, srid=2385)

        route = self.service.calculate_route(1, start, end)

        # --- 断言 ---
        self.assertIsNotNone(route)

        # 1. 验证路径长度：肯定大于直线距离 (16米)
        # 直线距离 = 18 - 2 = 16
        self.assertTrue(route.length > 16.0)

        # 2. 验证路径走向：必须经过左侧缺口
        # 获取路径上所有点的 x 坐标
        coords = route.coords
        min_x_in_path = min(p[0] for p in coords)

        # 因为墙是从 x=5 开始的，所以要想过去，路径中至少有一个点的 x 必须小于 5 (或者接近 5)
        # 我们这里断言 < 6.0 是为了留一点网格化精度的余量
        self.assertLess(min_x_in_path, 6.0)

    @patch('guide.services.GuideContext')
    def test_unreachable_target(self, MockContext):
        """测试终点被完全包围无法到达的情况"""
        mock_ctx_instance = MockContext.return_value

        # 障碍物完全包围终点 (10, 10)
        box = Polygon(((8, 8), (8, 12), (12, 12), (12, 8), (8, 8)), srid=2385)

        mock_ctx_instance.get_map_geometry_data.return_value = (self.map_boundary, [], [box])
        self.service.ctx = mock_ctx_instance

        start = Point(2, 2, srid=2385)
        end = Point(10, 10, srid=2385)  # 在盒子里面

        # 预期抛出 ValueError (因为 End node is not walkable)
        # 或者如果 End node 勉强算 walkable 但无法到达，则返回 None
        # 根据 services.py 逻辑，先检查 is_walkable

        # 由于障碍物占位，End point 所在的网格会被标记为 obstacle
        with self.assertRaises(ValueError) as cm:
            self.service.calculate_route(1, start, end)

        self.assertIn("End node is not walkable", str(cm.exception))


class GuideIntegrationTestCase(APITestCase):
    """
    第二步：集成测试
    测试 Views -> Services -> Context -> DB 的完整链路
    """

    def setUp(self):
        # 1. 创建基础建筑 (外键依赖)
        self.building = Building.objects.create(
            name="Test Mall",
            address="123 Test St"
        )

        # 2. 创建地图 (Map)
        # 地图是一个 20x20 的正方形
        # 注意：Map 的 detail 字段是 GeometryCollection
        boundary = Polygon(((0, 0), (0, 20), (20, 20), (20, 0), (0, 0)), srid=2385)
        gc = GeometryCollection(boundary, srid=2385)

        self.map_obj = Map.objects.create(
            building=self.building,
            floor_number=1,
            detail=gc
        )

        # 3. 创建一个商铺 (障碍物)
        # 商铺挡在地图中间 (8,8) 到 (12,12)
        store_shape = Polygon(((8, 8), (8, 12), (12, 12), (12, 8), (8, 8)), srid=2385)
        self.store = Storearea.objects.create(
            store_name="Blocker Store",
            owner_name="Test Owner",
            owner_phone="123",
            shape=store_shape,
            is_active=True  # 确保是激活状态
        )

        # 4. 关联商铺和地图 (建立中间表关系)
        # 注意：根据你的 models.py，StoreareaMap 有两个外键
        StoreareaMap.objects.create(
            storearea=self.store,
            map=self.map_obj
        )

        # API URL (需要你在 urls.py 中配置好，这里假设路径是 /api/guide/route/)
        self.url = '/api/guide/route/'

    def test_route_api_success(self):
        """测试完整的 API 调用流程"""
        # 起点 (2,2)，终点 (18,18)
        # 中间有商铺挡路，应该能规划出路径
        payload = {
            "map_id": self.map_obj.id,
            "start": {"x": 2.0, "y": 2.0},
            "end": {"x": 18.0, "y": 18.0}
        }

        response = self.client.post(self.url, payload, format='json')

        # 1. 验证状态码 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. 验证返回数据结构
        data = response.data
        self.assertIn("route", data)
        self.assertIn("distance", data)
        self.assertIsInstance(data["route"], dict)  # GeoJSON 对象
        self.assertIsInstance(data["route"]["coordinates"], list)

        # 3. 验证距离是否合理 (直线约22米，绕路肯定大于22米)
        self.assertTrue(data["distance"] > 22.0)

        # 打印一下结果看看
        print(f"\n[Integration Test] Route Distance: {data['distance']} meters")

    def test_api_missing_params(self):
        """测试参数缺失情况"""
        payload = {"map_id": self.map_obj.id}  # 缺少 start/end
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_invalid_coordinates(self):
        """测试无效坐标 (起点在墙里)"""
        # 起点 (10, 10) 正好在刚才创建的 Storearea 内部
        payload = {
            "map_id": self.map_obj.id,
            "start": {"x": 10.0, "y": 10.0},
            "end": {"x": 18.0, "y": 18.0}
        }
        response = self.client.post(self.url, payload, format='json')

        # 预期报错：Start node is not walkable
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)