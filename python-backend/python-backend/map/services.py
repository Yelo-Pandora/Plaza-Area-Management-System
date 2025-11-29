from core.models import *
from .context import MapContext


class MapServices:
    def __init__(self):
        self.context = MapContext()

    def get_map_list(self):
        """
        调用 Context 获取数据，这里可以添加额外的业务逻辑，
        例如：筛选 active 的地图，或者根据用户权限过滤。
        """
        maps = self.context.list_all_maps()

        # 示例：如果未来有业务逻辑需要过滤掉没有 detail 的地图
        # maps = [m for m in maps if m.detail is not None]

        return maps

    def get_single_map(self, map_id):
        """
        获取单个地图的业务逻辑
        """
        return self.context.get_map_by_id(map_id)