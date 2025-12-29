from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.gis.geos import Polygon, GeometryCollection
from core.models import Building, Map, Storearea, StoreareaMap


class MapViewSetTestCase(APITestCase):
    """
    测试 MapViewSet 的 list 和 retrieve 接口
    验证从数据库到 Service 再到 View 的数据流是否正常
    """

    def setUp(self):
        """
        测试数据准备：
        1. 创建 Building
        2. 创建 Map (带 GeometryCollection)
        3. 创建 Storearea (带 Polygon)
        4. 建立 Map 和 Storearea 的关联
        """
        # 1. 创建建筑
        self.building = Building.objects.create(
            name="测试万达广场",
            address="上海市杨浦区"
        )

        # 2. 创建地图底图几何 (SRID 2385)
        # 假设是一个 100x100 的正方形外轮廓
        outer_shell = Polygon(((0, 0), (0, 100), (100, 100), (100, 0), (0, 0)), srid=2385)
        # detail 字段是 GeometryCollection
        map_detail = GeometryCollection(outer_shell, srid=2385)

        self.map_obj = Map.objects.create(
            building=self.building,
            floor_number=1,
            detail=map_detail
        )

        # 3. 创建商铺
        # 在地图内部创建一个 10x10 的小方块商铺
        store_shape = Polygon(((10, 10), (10, 20), (20, 20), (20, 10), (10, 10)), srid=2385)
        self.store = Storearea.objects.create(
            store_name="测试海底捞",
            type=1,
            shape=store_shape,
            owner_name="张三",
            owner_phone="123456",
            is_active = True
        )

        # 4. 关联商铺到地图
        StoreareaMap.objects.create(
            map=self.map_obj,
            storearea=self.store
        )

        self.list_url = reverse('map-list')
        self.detail_url = reverse('map-detail', args=[self.map_obj.id])

    def test_list_maps(self):
        """
        测试获取地图列表 (GET /api/maps/)
        """
        response = self.client.get(self.list_url)

        # 1. 验证状态码
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. 验证返回数据类型是列表
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)

        # 3. 验证基础字段
        map_data = response.data[0]
        self.assertEqual(map_data['floor_number'], 1)
        self.assertEqual(map_data['building_name'], "测试万达广场")

        # 4. 验证列表接口是否正确处理了 temp_stores
        if 'stores' in map_data:
            self.assertIsInstance(map_data['stores'], list)

    def test_retrieve_map_success(self):
        """
        测试获取单张地图详情 (GET /api/maps/{id}/)
        核心：验证 Service 是否成功组装了 detail_geojson 和 stores
        """
        response = self.client.get(self.detail_url)

        # 1. 验证状态码
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data

        # 2. 验证底图几何 (detail_geojson)
        self.assertIn('detail_geojson', data)
        self.assertEqual(data['detail_geojson']['type'], 'GeometryCollection')

        # 3. 验证关联元素 (stores)
        # 这是验证 MapDisplayService.get_full_map_details 逻辑的关键
        self.assertIn('stores', data)
        self.assertEqual(len(data['stores']), 1)

        store_data = data['stores'][0]
        self.assertEqual(store_data['store_name'], "测试海底捞")
        self.assertEqual(store_data['id'], self.store.id)

        # 验证商铺的几何是否被正确序列化为 GeoJSON
        self.assertIn('geometry', store_data)
        self.assertEqual(store_data['geometry']['type'], 'Polygon')

        # 4. 验证其他空列表字段是否存在 (facilities, events, etc.)
        self.assertIn('facilities', data)
        self.assertEqual(data['facilities'], [])  # setUp中没创建设施，应为空列表

    def test_retrieve_map_not_found(self):
        """
        测试获取不存在的地图 ID
        """
        non_existent_url = reverse('map-detail', args=[99999])
        response = self.client.get(non_existent_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)