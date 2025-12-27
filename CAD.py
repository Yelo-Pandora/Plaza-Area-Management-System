import ezdxf
import math

def create_complex_plaza_dxf():
    # 1. 创建 DXF 文档 (R2010版本兼容性极佳)
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # 2. 定义图层 (Layer) - 严格对应后端 MapEditorService.LAYER_MAPPING
    # 颜色: 1:红, 2:黄, 3:绿, 4:青, 5:蓝, 6:洋红, 7:白
    layers = [
        ('FLOOR_OUTLINE', 7), # 地板
        ('VOIDS', 1),         # 镂空
        ('AREA_STORE', 5),    # 店铺 (蓝色)
        ('AREA_EVENT', 3),    # 活动 (绿色)
        ('AREA_OTHER', 6),    # 其他 (洋红)
        ('FACILITIES', 2)     # 设施 (黄色)
    ]
    for name, color in layers:
        if name not in doc.layers:
            doc.layers.add(name=name, color=color)

    # 辅助函数：添加闭合多段线和文字标签
    def add_area(points, layer, label, text_pos=None):
        # 添加闭合多段线
        polyline = msp.add_lwpolyline(points, close=True, dxfattribs={'layer': layer})

        # 计算大致中心用于放文字
        if text_pos is None:
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            text_pos = (sum(xs)/len(xs), sum(ys)/len(ys))
        
        # 添加文字标签
        msp.add_text(label, height=500, dxfattribs={'layer': layer}).set_placement(text_pos)

    # ==========================================
    # 3. 绘制地板外轮廓 (FLOOR_OUTLINE)
    # 场景：一个 80m x 60m 的大型不规则建筑
    # 形状：左边突出，右上角切角，下方内凹入口
    # ==========================================
    floor_points = [
        (0, 20000),      # 左下起点
        (0, 50000),      # 左上
        (10000, 50000),  # 向右
        (10000, 60000),  # 向上突出
        (50000, 60000),  # 顶部横向
        (80000, 40000),  # 右上切角 (斜边)
        (80000, 0),      # 右下
        (50000, 0),      # 底部右
        (50000, 5000),   # 底部内凹 (入口区)
        (30000, 5000),   # 底部内凹
        (30000, 0),      # 底部左
        (15000, 0),      # ...
        (15000, 20000)   # 回到左侧突出部底部
    ]
    add_area(floor_points, 'FLOOR_OUTLINE', 'Level 1 Floor')

    # ==========================================
    # 4. 绘制镂空/中庭 (VOIDS)
    # 场景：中央大中庭，视线通透，形状为不规则六边形
    # ==========================================
    void_points = [
        (35000, 25000),
        (45000, 25000),
        (50000, 30000),
        (45000, 35000),
        (35000, 35000),
        (30000, 30000)
    ]
    add_area(void_points, 'VOIDS', 'Central Atrium')

    # ==========================================
    # 5. 绘制店铺 (AREA_STORE)
    # 场景：沿墙分布，形状各异
    # ==========================================
    
    # 店铺1：左侧 L 型大店铺 (例如超市)
    store1 = [
        (2000, 22000),
        (13000, 22000),
        (13000, 35000),
        (8000, 35000),
        (8000, 48000),
        (2000, 48000)
    ]
    add_area(store1, 'AREA_STORE', 'Supermarket')

    # 店铺2：右下角梯形店铺 (例如咖啡厅)
    store2 = [
        (65000, 2000),
        (78000, 2000),
        (78000, 15000),
        (65000, 12000)  # 斜边
    ]
    add_area(store2, 'AREA_STORE', 'Cafe')

    # 店铺3：上方条形店铺
    store3 = [
        (15000, 52000),
        (35000, 52000),
        (35000, 58000),
        (15000, 58000)
    ]
    add_area(store3, 'AREA_STORE', 'Fashion Store')

    # ==========================================
    # 6. 绘制活动区域 (AREA_EVENT)
    # 场景：位于中庭下方，人流汇聚处，形状稍微复杂一点
    # ==========================================
    event_points = [
        (35000, 10000), # 底部
        (45000, 10000),
        (48000, 15000), # 凸出
        (45000, 20000), # 顶部
        (35000, 20000),
        (32000, 15000)  # 凸出
    ]
    add_area(event_points, 'AREA_EVENT', 'Main Stage')

    # ==========================================
    # 7. 绘制其他区域 (AREA_OTHER)
    # 场景：办公区或仓库，位于较偏僻的右上角斜边处
    # ==========================================
    other_points = [
        (60000, 45000),
        (70000, 45000),
        (75000, 41000), # 顺应楼层轮廓的斜边
        (60000, 41000)
    ]
    add_area(other_points, 'AREA_OTHER', 'Admin Office')

    # ==========================================
    # 8. 绘制设施 (FACILITIES)
    # 后端逻辑：读取 CIRCLE 或 POINT。
    # 这里我们用圆表示，圆心即坐标。
    # ==========================================
    
    facilities = [
        # 服务台 (Info): 入口正对面
        {"pos": (40000, 8000), "r": 800, "label": "Info Desk (Type 3)"},
        
        # 电梯 (Elevator): 核心筒，通常成组出现
        {"pos": (12000, 55000), "r": 1000, "label": "Elevator 1 (Type 0)"},
        {"pos": (55000, 55000), "r": 1000, "label": "Elevator 2 (Type 0)"},
        
        # 卫生间 (Restroom): 角落
        {"pos": (75000, 10000), "r": 900, "label": "WC (Type 1)"},
        {"pos": (5000, 25000), "r": 900, "label": "WC (Type 1)"},
        
        # 安全出口 (Exit): 远离中心的边缘
        {"pos": (2000, 21000), "r": 600, "label": "Exit (Type 2)"},
        {"pos": (78000, 38000), "r": 600, "label": "Exit (Type 2)"},
        {"pos": (40000, 59000), "r": 600, "label": "Exit (Type 2)"},

        # 其他设施 (Other): 比如自动售货机
        {"pos": (52000, 28000), "r": 500, "label": "Vending (Type 4)"}
    ]

    for fac in facilities:
        # 【修正3】使用 dxfattribs 传递图层
        msp.add_circle(fac["pos"], radius=fac["r"], dxfattribs={'layer': 'FACILITIES'})
        
        msp.add_point(fac["pos"], dxfattribs={'layer': 'FACILITIES'})
        
        msp.add_text(fac["label"], height=300, dxfattribs={'layer': 'FACILITIES'}).set_placement(
            (fac["pos"][0] - 500, fac["pos"][1] + fac["r"] + 200)
        )

    filename = "complex_plaza.dxf"
    doc.saveas(filename)
    print(f"成功生成 CAD 文件: {filename}")
    print(f"包含图层: {[l[0] for l in layers]}")
    print("请在前端选择 'CAD 导入' 并上传此文件。")

if __name__ == "__main__":
    create_complex_plaza_dxf()