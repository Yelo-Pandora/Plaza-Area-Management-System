from .context import StoreareaContext, EventContext, EventareaContext, OtherareaContext,FacilityContext
from map.context import MapContext
from django.contrib.gis.geos import GeometryCollection, Polygon, Point
from django.db import transaction
import ezdxf
import io


class StoreareaService:
    """
    店铺区域（Storearea）的业务层
    负责处理业务逻辑，调用数据访问层方法，仅处理shape属性相关操作
    """

    @staticmethod
    def get_all_storeareas():
        """获取所有店铺区域"""
        return StoreareaContext.get_all()

    @staticmethod
    def get_storearea_by_id(storearea_id):
        """根据ID获取店铺区域"""
        return StoreareaContext.get_by_id(storearea_id)

    @staticmethod
    def create_storearea(shape, map_id=None):
        """创建新的店铺区域，并可选绑定到指定地图"""
        return StoreareaContext.create(shape, map_id)

    @staticmethod
    def update_shape(storearea_id, shape):
        """更新店铺区域的形状"""
        # 可以在这里添加业务逻辑验证
        return StoreareaContext.update_shape(storearea_id, shape)

    @staticmethod
    def delete_storearea(storearea_id):
        """删除店铺区域"""
        # 可以在这里添加业务逻辑验证
        return StoreareaContext.delete(storearea_id)

    @staticmethod
    def get_events_for_storearea(storearea_id):
        """获取店铺关联的所有活动ID"""
        return StoreareaContext.get_events_by_storearea(storearea_id)


class EventService:
    """
    活动（Event）的业务层
    负责处理业务逻辑，调用数据访问层方法，仅处理shape属性相关操作
    """

    @staticmethod
    def get_all_events():
        """获取所有活动"""
        return EventContext.get_all()

    @staticmethod
    def get_event_by_id(event_id):
        """根据ID获取活动"""
        return EventContext.get_by_id(event_id)



    @staticmethod
    def get_areas_for_event(event_id):
        """获取活动关联的所有区域ID（包括店铺区域和活动区域）"""
        storearea_ids = EventContext.get_storeareas_by_event(event_id)
        eventarea_ids = EventContext.get_eventareas_by_event(event_id)
        return {
            'storearea_ids': storearea_ids,
            'eventarea_ids': eventarea_ids,
            'all_area_ids': storearea_ids + eventarea_ids
        }

    @staticmethod
    def add_storearea_to_event(event_id, storearea_id):
        """添加活动与店铺区域的关联关系"""
        # 可以在这里添加业务逻辑验证（如检查活动和店铺是否存在等）
        return EventContext.add_storearea_relation(event_id, storearea_id)

    @staticmethod
    def remove_storearea_from_event(event_id, storearea_id):
        """移除活动与店铺区域的关联关系"""
        # 可以在这里添加业务逻辑验证
        return EventContext.remove_storearea_relation(event_id, storearea_id)

    @staticmethod
    def add_eventarea_to_event(event_id, eventarea_id):
        """添加活动与活动区域的关联关系"""
        # 可以在这里添加业务逻辑验证（如检查活动和活动区域是否存在等）
        return EventContext.add_eventarea_relation(event_id, eventarea_id)

    @staticmethod
    def remove_eventarea_from_event(event_id, eventarea_id):
        """移除活动与活动区域的关联关系"""
        # 可以在这里添加业务逻辑验证
        return EventContext.remove_eventarea_relation(event_id, eventarea_id)


class EventareaService:
    """
    活动区域（Eventarea）的业务层
    负责处理业务逻辑，调用数据访问层方法
    注意：在editor模块中只处理shape属性的更新
    """

    @staticmethod
    def get_all_eventareas():
        """获取所有活动区域"""
        return EventareaContext.get_all()

    @staticmethod
    def get_eventarea_by_id(eventarea_id):
        """根据ID获取活动区域"""
        return EventareaContext.get_by_id(eventarea_id)

    @staticmethod
    def create_eventarea(shape, map_id=None):
        """创建新的活动区域，并可选绑定到指定地图"""
        return EventareaContext.create(shape, map_id)

    @staticmethod
    def update_eventarea_shape(eventarea_id, shape):
        """更新活动区域的形状"""
        # 可以在这里添加业务逻辑验证（如形状有效性检查等）
        return EventareaContext.update_shape(eventarea_id, shape)

    @staticmethod
    def delete_eventarea(eventarea_id):
        """删除活动区域"""
        # 可以在这里添加业务逻辑验证
        return EventareaContext.delete(eventarea_id)


class OtherareaService:
    """
    其他区域（Otherarea）的业务层
    负责处理业务逻辑，调用数据访问层方法
    注意：在editor模块中只处理shape属性的更新
    """

    @staticmethod
    def get_all_otherareas():
        """获取所有其他区域"""
        return OtherareaContext.get_all()

    @staticmethod
    def get_otherarea_by_id(otherarea_id):
        """根据ID获取其他区域"""
        return OtherareaContext.get_by_id(otherarea_id)

    @staticmethod
    def create_otherarea(shape, map_id=None, type_val=None):
        """创建新的其他区域，并可选绑定到指定地图"""
        return OtherareaContext.create(shape, map_id, type_val)

    @staticmethod
    def update_otherarea_shape(otherarea_id, shape):
        """更新其他区域的形状"""
        # 可以在这里添加业务逻辑验证（如形状有效性检查等）
        return OtherareaContext.update_shape(otherarea_id, shape)

    @staticmethod
    def delete_otherarea(otherarea_id):
        """删除其他区域"""
        # 可以在这里添加业务逻辑验证
        return OtherareaContext.delete(otherarea_id)

class FacilityService:
    """
    设施（Facility）的业务层
    """
    @staticmethod
    def get_all_facilities():
        return FacilityContext.get_all()

    @staticmethod
    def get_facility_by_id(facility_id):
        return FacilityContext.get_by_id(facility_id)

    @staticmethod
    def create_facility(location, map_id=None, type_val=None):
        return FacilityContext.create(location, map_id, type_val)

    @staticmethod
    def update_facility_location(facility_id, location):
        return FacilityContext.update_location(facility_id, location)

    @staticmethod
    def delete_facility(facility_id):
        return FacilityContext.delete(facility_id)


class MapEditorService:
    """
    地图编辑服务：处理地图及关联要素的创建、导入
    """

    # 定义 CAD 图层名称到业务类型的映射
    LAYER_MAPPING = {
        'FLOOR_OUTLINE': 'floor',  # 底图外框
        'VOIDS': 'hole',  # 底图镂空
        'AREA_STORE': 'storearea',  # 店铺区域
        'AREA_EVENT': 'eventarea',  # 活动区域
        'AREA_OTHER': 'otherarea',  # 其他区域
        'FACILITIES': 'facility'  # 设施
    }

    @staticmethod
    def create_map(building_id, floor_number, file=None):
        map_ctx = MapContext()

        # 1. 业务校验
        if map_ctx.check_exists(building_id, floor_number):
            raise ValueError("该建筑的此楼层已存在地图")

        try:
            with transaction.atomic():
                # 2. 解析 DXF 数据
                if file:
                    dxf_data = MapEditorService._parse_dxf_layers(file)
                else:
                    # 手动模式默认数据
                    dxf_data = {
                        'floor': Polygon(((0, 0), (0, 100), (100, 100), (100, 0), (0, 0)), srid=2385),
                        'holes': [],
                        'storearea': [],
                        'eventarea': [],
                        'otherarea': [],
                        'facility': []
                    }

                # 3. 组装并创建 Map (底图)
                # 将外框和镂空组合成 GeometryCollection
                if not dxf_data['floor']:
                    raise ValueError("DXF 中未找到 FLOOR_OUTLINE 图层或有效的闭合外轮廓")

                # 组合 list: [外框, 洞1, 洞2...]
                map_geometry_list = [dxf_data['floor']] + dxf_data['holes']
                map_geometry = GeometryCollection(map_geometry_list, srid=2385)

                # 调用 Context 创建地图
                new_map = map_ctx.create_map_record(building_id, floor_number, map_geometry)

                # 4. 创建关联实体 (调用 editor.context 中的各 Context)
                # 注意：editor.context.create 方法通常只接收 shape/location 和 map_id

                # A. 创建店铺
                for shape in dxf_data['storearea']:
                    # 这里可以根据需求生成默认名称，例如 "导入的店铺"
                    StoreareaContext.create(shape=shape, map_id=new_map.id)

                # B. 创建活动区
                for shape in dxf_data['eventarea']:
                    EventareaContext.create(shape=shape, map_id=new_map.id)

                # C. 创建其他区域
                for shape in dxf_data['otherarea']:
                    # type_val 默认为 0
                    OtherareaContext.create(shape=shape, map_id=new_map.id, type_val=0)

                # D. 创建设施 (点)
                for location in dxf_data['facility']:
                    # FacilityContext.create 接收 Point 对象
                    FacilityContext.create(location=location, map_id=new_map.id, type_val=0)

                return new_map

        except Exception as e:
            # 捕获异常并回滚事务（由 transaction.atomic 自动处理回滚，这里重新抛出以便 View 层捕获）
            raise ValueError(f"创建地图失败: {str(e)}")

    @staticmethod
    def _parse_dxf_layers(uploaded_file):
        """
        解析 DXF 文件，按图层分类提取几何数据
        """
        try:
            # === 修复逻辑开始 ===
            # 1. 统一转换为二进制流 (Binary Stream)
            binary_stream = None
            if isinstance(uploaded_file, bytes):
                binary_stream = io.BytesIO(uploaded_file)
            elif hasattr(uploaded_file, 'read'):
                # 已经是流对象 (BytesIO 或 Django UploadedFile)
                binary_stream = uploaded_file
            else:
                raise ValueError("不支持的文件输入类型")

            # 2. 确保指针在开头
            if hasattr(binary_stream, 'seek'):
                binary_stream.seek(0)

            # 3. 将二进制流包装为文本流 (Text Stream)
            # ezdxf.read() 需要读取字符串。DXF 通常是 cp1252 或 utf-8。
            # 使用 errors='ignore' 防止因为编码问题导致解析完全失败
            text_stream = io.TextIOWrapper(binary_stream, encoding='utf-8', errors='ignore')

            # 4. 读取 DXF
            doc = ezdxf.read(text_stream)
            # === 修复逻辑结束 ===

            msp = doc.modelspace()

            result = {
                'floor': None,
                'holes': [],
                'storearea': [],
                'eventarea': [],
                'otherarea': [],
                'facility': []
            }

            # 遍历所有实体
            for entity in msp:
                # 增加容错：有些实体可能没有 layer 属性
                if not hasattr(entity.dxf, 'layer'):
                    continue

                layer_name = entity.dxf.layer.upper()

                if layer_name not in MapEditorService.LAYER_MAPPING:
                    continue

                target_type = MapEditorService.LAYER_MAPPING[layer_name]

                # --- 处理多边形 (区域/楼层) ---
                if entity.dxftype() == 'LWPOLYLINE':
                    if not entity.closed:
                        continue  # 忽略未闭合的线

                    points = []
                    # 坐标转换：毫米 -> 米
                    for p in entity.get_points():
                        points.append((p[0] / 1000.0, p[1] / 1000.0))

                    # 确保首尾闭合
                    if points[0] != points[-1]:
                        points.append(points[0])

                    if len(points) >= 4:
                        poly = Polygon(points, srid=2385)

                        if target_type == 'floor':
                            # 假设图纸里只有一个最大的框是地板，如果有多个，暂取第一个或覆盖
                            if result['floor'] is None:
                                result['floor'] = poly
                            else:
                                # 如果有多个 FLOOR_OUTLINE，简单的逻辑是看谁面积大
                                if poly.area > result['floor'].area:
                                    result['floor'] = poly
                        elif target_type == 'hole':
                            result['holes'].append(poly)
                        elif target_type in ['storearea', 'eventarea', 'otherarea']:
                            result[target_type].append(poly)

                # --- 处理点/圆 (设施) ---
                elif entity.dxftype() in ['CIRCLE', 'POINT']:
                    if target_type == 'facility':
                        x, y = 0, 0
                        if entity.dxftype() == 'CIRCLE':
                            # 圆取圆心
                            center = entity.dxf.center
                            x, y = center.x / 1000.0, center.y / 1000.0
                        else:
                            # 点取坐标
                            loc = entity.dxf.location
                            x, y = loc.x / 1000.0, loc.y / 1000.0

                        point = Point(x, y, srid=2385)
                        result['facility'].append(point)

            return result

        except Exception as e:
            # 增加一些调试信息
            import traceback
            traceback.print_exc()
            raise ValueError(f"DXF 解析内部错误: {str(e)}")

    @staticmethod
    def delete_map(map_id):
        """
        删除地图及其所有关联的实体（商铺、设施等）
        严格遵守 Service -> Context -> Model 分层，不直接访问 Model
        """
        map_ctx = MapContext()

        # 1. 检查地图是否存在
        map_obj = map_ctx.get_by_id(map_id)
        if not map_obj:
            raise ValueError("地图不存在")

        try:
            with transaction.atomic():
                # 2. 获取关联的元素 ID (通过 Context)
                # get_map_elements 返回 (store_ids, facility_ids, other_ids, event_ids)
                s_ids, f_ids, o_ids, e_ids = map_ctx.get_map_elements(map_obj)

                # 3. 通过各领域的 Context 批量删除实体
                # 注意：StoreareaMap 等中间表会因级联删除自动清理，
                # 但 Storearea 实体本身需要显式删除。

                if s_ids:
                    StoreareaContext.delete_many(s_ids)

                if f_ids:
                    FacilityContext.delete_many(f_ids)

                if o_ids:
                    OtherareaContext.delete_many(o_ids)

                if e_ids:
                    EventareaContext.delete_many(e_ids)

                # 4. 通过 Context 删除地图本身
                map_ctx.delete_map(map_id)

        except Exception as e:
            # 记录日志等
            raise ValueError(f"删除地图失败: {str(e)}")