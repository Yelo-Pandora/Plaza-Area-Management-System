import { watchPostEffect, onUnmounted, nextTick } from 'vue'
import { useMapEditorStore } from '../../composables/useMapEditorStore'
import * as managementAPI from '@/api/management'
import * as KonvaImport from 'konva'

// --- 1. Konva 导入兼容性处理 (核心修复) ---
// 解决 Vite/Rollup 打包后可能出现的 default 嵌套问题
const getKonva = () => {
  let k = KonvaImport
  // 递归查找，直到找到 Stage 构造函数
  // 最多尝试 3 层，避免死循环
  for (let i = 0; i < 3; i++) {
    if (k.Stage) return k
    if (k.default) k = k.default
    else break
  }
  // 兜底：尝试使用全局挂载的对象 (vue-konva 可能挂载了)
  if (window.Konva) return window.Konva
  return k
}

const Konva = getKonva()

export function useCanvasLogic(stageContainerRef) {
  const {
    currentMap,
    loading,
    storeareas,
    eventareas,
    otherareas,
    facilities,
    selectedFeature,
    selectedType,
    selectFeature
  } = useMapEditorStore()

  let stage = null
  let layer = null
  let shapesLayer = null

  // 类型颜色配置
  const typeColors = {
    storearea: '#2563eb',
    eventarea: '#16a34a',
    otherarea: '#f97316',
    facility: '#8b5cf6',
  }

  // --- 2. 自动适配视图 (防止图形画在屏幕外) ---
  const autoFitView = () => {
    if (!stage || !shapesLayer) return

    // 获取所有图形的边界框
    const box = shapesLayer.getClientRect({ skipTransform: true })

    // 如果没有图形或图形为空，重置视图
    if (box.width === 0 || box.height === 0) {
      stage.position({ x: 0, y: 0 })
      stage.scale({ x: 1, y: 1 })
      return
    }

    const padding = 50
    const stageWidth = stage.width()
    const stageHeight = stage.height()

    // 计算缩放比例
    const scaleX = (stageWidth - padding * 2) / box.width
    const scaleY = (stageHeight - padding * 2) / box.height
    const scale = Math.min(scaleX, scaleY) // 保持纵横比

    // 计算居中位置
    const centerX = stageWidth / 2 - (box.x + box.width / 2) * scale
    const centerY = stageHeight / 2 - (box.y + box.height / 2) * scale

    // 应用变换
    stage.position({ x: centerX, y: centerY })
    stage.scale({ x: scale, y: scale })
    stage.batchDraw()

    console.log(`[AutoFit] 视图已自动适配。缩放: ${scale.toFixed(2)}, 位移: (${centerX.toFixed(0)}, ${centerY.toFixed(0)})`)
  }

  // --- 3. 绘制逻辑 ---

  // 绘制单个多边形区域
  const drawPolygon = (area, type) => {
    if (!area.geometry || !area.geometry.coordinates) return

    let points = []
    // 解析 GeoJSON Polygon / MultiPolygon
    if (area.geometry.type === 'Polygon') {
      points = area.geometry.coordinates[0].flat()
    } else if (area.geometry.type === 'MultiPolygon') {
      points = area.geometry.coordinates[0][0].flat()
    }

    if (points.length < 4) return // 至少需要2个点(x,y)

    const color = typeColors[type]

    // 创建多边形
    const poly = new Konva.Line({
      points: points,
      closed: true,
      fill: `${color}33`, // 20% 透明度
      stroke: color,
      strokeWidth: 1 / (stage ? stage.scaleX() : 1), // 保持线条视觉宽度一致
      draggable: true,
      name: 'feature-shape', // 用于查找
      id: `${type}-${area.id}`,
      hitStrokeWidth: 10 // 增加点击判定范围
    })

    // 选中高亮状态
    if (selectedFeature.value?.id === area.id && selectedType.value === type) {
      poly.strokeWidth(3 / (stage ? stage.scaleX() : 1))
      poly.fill(`${color}66`)
      poly.shadowColor('black')
      poly.shadowBlur(10)
      poly.shadowOpacity(0.3)
      poly.moveToTop()
    }

    // 事件绑定
    poly.on('click tap', (e) => {
      e.cancelBubble = true
      selectFeature(type, area)
    })

    poly.on('dragend', function() {
      handleGeometryUpdate(type, area, this)
    })

    // 鼠标悬停效果
    poly.on('mouseenter', () => {
      stage.container().style.cursor = 'pointer'
      if (selectedFeature.value?.id !== area.id) {
        poly.fill(`${color}55`)
        shapesLayer.batchDraw()
      }
    })

    poly.on('mouseleave', () => {
      stage.container().style.cursor = 'default'
      if (selectedFeature.value?.id !== area.id) {
        poly.fill(`${color}33`)
        shapesLayer.batchDraw()
      }
    })

    shapesLayer.add(poly)
  }

  // 绘制设施 (点/圆形)
  const drawFacility = (facility) => {
    let x = 0, y = 0

    if (facility.location && typeof facility.location.x === 'number') {
      x = facility.location.x
      y = facility.location.y
    } else if (facility.geometry && facility.geometry.type === 'Point') {
      x = facility.geometry.coordinates[0]
      y = facility.geometry.coordinates[1]
    } else {
      return
    }

    const color = typeColors['facility']
    // 设施大小稍微固定一点，不随缩放变得过大/过小
    const radius = 5 / (stage ? stage.scaleX() : 1)

    const circle = new Konva.Circle({
      x, y,
      radius: Math.max(radius, 2), // 最小半径2
      fill: color,
      stroke: 'white',
      strokeWidth: 1,
      draggable: true,
      id: `facility-${facility.id}`
    })

    if (selectedFeature.value?.id === facility.id && selectedType.value === 'facility') {
      circle.stroke('yellow')
      circle.strokeWidth(2)
      circle.shadowBlur(5)
    }

    circle.on('click tap', (e) => {
      e.cancelBubble = true
      selectFeature('facility', facility)
    })

    circle.on('dragend', function() {
      // 更新设施位置逻辑...
      // 简单实现：仅更新本地，后端保存逻辑同上
      facility.location = { x: this.x(), y: this.y() }
    })

    shapesLayer.add(circle)
  }

  // 绘制所有图层
  const drawAllFeatures = () => {
    if (!shapesLayer) return
    shapesLayer.destroyChildren()

    storeareas.value.forEach(a => drawPolygon(a, 'storearea'))
    eventareas.value.forEach(a => drawPolygon(a, 'eventarea'))
    otherareas.value.forEach(a => drawPolygon(a, 'otherarea'))
    facilities.value.forEach(f => drawFacility(f))

    shapesLayer.batchDraw()
  }

  // --- 4. 数据保存逻辑 ---
  const handleGeometryUpdate = async (type, area, shapeNode) => {
    // 计算绝对坐标 (Points是相对的 + 拖拽后的偏移 x/y)
    const points = shapeNode.points()
    const dx = shapeNode.x()
    const dy = shapeNode.y()

    const newCoords = []
    for (let i = 0; i < points.length; i += 2) {
      newCoords.push([points[i] + dx, points[i+1] + dy])
    }

    // 确保闭合
    if (newCoords.length > 0) {
      const start = newCoords[0]
      const end = newCoords[newCoords.length - 1]
      if (start[0] !== end[0] || start[1] !== end[1]) {
        newCoords.push([...start])
      }
    }

    // 更新本地数据引用
    area.geometry = { type: 'Polygon', coordinates: [newCoords] }

    // 重置节点位置 (偏移量已合入坐标)
    shapeNode.position({ x: 0, y: 0 })
    shapeNode.points(newCoords.flat())
    shapesLayer.batchDraw()

    console.log(`[Save] 更新 ${type} ID:${area.id} 几何数据`)

    // TODO: 调用API保存 (视后端接口而定)
    try {
      const apiMap = {
        storearea: managementAPI.updateManagementStorearea,
        eventarea: managementAPI.updateManagementEventarea,
        otherarea: managementAPI.updateManagementOtherarea
      }
      if (apiMap[type]) {
        // 注意：后端可能需要特定格式，这里假设接受 geometry 对象
        // await apiMap[type](area.id, { geometry: area.geometry })
      }
    } catch (e) {
      console.error('保存失败', e)
    }
  }

  // --- 5. 核心初始化逻辑 ---
  const initKonva = () => {
    const container = stageContainerRef.value

    // 双重检查：必须 DOM 存在 且 数据存在
    if (!container || !currentMap.value) {
      return
    }

    // 获取实际尺寸
    const width = container.clientWidth
    const height = container.clientHeight

    if (width === 0 || height === 0) {
      console.warn('[Konva] 容器尺寸为 0，可能被隐藏或布局未完成')
      return
    }

    console.log(`[Konva] 初始化舞台: ${width}x${height}, 地图ID: ${currentMap.value.id}`)

    if (stage) stage.destroy()

    stage = new Konva.Stage({
      container,
      width,
      height,
      draggable: true
    })

    layer = new Konva.Layer()
    shapesLayer = new Konva.Layer() // 专门放图形

    // 背景层（用于接收拖拽平移事件）
    const bg = new Konva.Rect({
      x: -50000, y: -50000, width: 100000, height: 100000,
      fill: '#f8fafc' // 浅灰背景
    })

    // 点击背景取消选中
    bg.on('click', () => {
      selectFeature('', null)
    })

    layer.add(bg)
    stage.add(layer)
    stage.add(shapesLayer)

    // 滚轮缩放逻辑
    stage.on('wheel', (e) => {
      e.evt.preventDefault()
      const scaleBy = 1.1
      const oldScale = stage.scaleX()
      const pointer = stage.getPointerPosition()

      const mousePointTo = {
        x: (pointer.x - stage.x()) / oldScale,
        y: (pointer.y - stage.y()) / oldScale,
      }

      const direction = e.evt.deltaY > 0 ? -1 : 1 // 向下滚动缩小，向上滚动放大
      const newScale = direction > 0 ? oldScale * scaleBy : oldScale / scaleBy

      stage.scale({ x: newScale, y: newScale })

      const newPos = {
        x: pointer.x - mousePointTo.x * newScale,
        y: pointer.y - mousePointTo.y * newScale,
      }
      stage.position(newPos)
    })

    drawAllFeatures()

    // 初始化完成后，自动适应视图
    autoFitView()
  }

  // --- 6. 响应式监听 (核心修复) ---
  // 使用 watchPostEffect 确保在 DOM 更新后执行
  watchPostEffect(() => {
    const isReady = currentMap.value && stageContainerRef.value && !loading.value

    if (isReady) {
      // 只有当 ID 变化或 Stage 不存在时才彻底重置
      if (!stage || (stage && stage.attrs.mapId !== currentMap.value.id)) {
        initKonva()
        if (stage) stage.attrs.mapId = currentMap.value.id // 标记当前 ID
      } else {
        // 如果 Stage 还在，只是数据变了（比如选中状态、新增区域），只重绘图层
        drawAllFeatures()
      }
    }
  })

  onUnmounted(() => {
    if (stage) stage.destroy()
  })

  return {
    // 如果需要暴露方法给组件，可以在这里返回
    autoFitView
  }
}
