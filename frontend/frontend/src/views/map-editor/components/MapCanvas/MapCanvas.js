import { watchPostEffect, onUnmounted, nextTick } from 'vue'
import { useMapEditorStore } from '../../composables/useMapEditorStore'
import * as managementAPI from '@/api/management'
import * as KonvaImport from 'konva'

// --- 1. Konva 导入兼容性处理 ---
const getKonva = () => {
  let k = KonvaImport
  for (let i = 0; i < 3; i++) {
    if (k.Stage) return k
    if (k.default) k = k.default
    else break
  }
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
  let layer = null       // 背景层 (用于点击空白处取消选中)
  let baseLayer = null   // 新增：底图层 (建筑轮廓、墙体、镂空)
  let shapesLayer = null // 交互层 (店铺、活动区、设施)

  // 类型颜色配置
  const typeColors = {
    storearea: '#2563eb',
    eventarea: '#16a34a',
    otherarea: '#f97316',
    facility: '#8b5cf6',
  }

  // --- 2. 自动适配视图 ---
  const autoFitView = () => {
    // 优先适配底图，如果没有底图则适配所有内容
    const targetLayer = (baseLayer && baseLayer.hasChildren()) ? baseLayer : shapesLayer

    if (!stage || !targetLayer) return

    // 获取内容的边界框
    const box = targetLayer.getClientRect({ skipTransform: true })

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
    const scale = Math.min(scaleX, scaleY)

    // 计算居中位置
    const centerX = stageWidth / 2 - (box.x + box.width / 2) * scale
    const centerY = stageHeight / 2 - (box.y + box.height / 2) * scale

    stage.position({ x: centerX, y: centerY })
    stage.scale({ x: scale, y: scale })
    stage.batchDraw()
  }

  // --- 3. 绘制逻辑 ---

  // 新增：绘制底图 (建筑轮廓)
  const drawBaseMap = () => {
    if (!baseLayer || !currentMap.value || !currentMap.value.detail_geojson) return

    baseLayer.destroyChildren()

    const geojson = currentMap.value.detail_geojson
    // 后端返回的是 GeometryCollection
    // 约定：索引 0 是外轮廓 (地板)，索引 1+ 是内部镂空 (中庭等)

    let geometries = []
    if (geojson.type === 'GeometryCollection') {
      geometries = geojson.geometries
    } else if (geojson.type === 'Polygon' || geojson.type === 'MultiPolygon') {
      // 兼容可能只返回单个 Polygon 的情况
      geometries = [geojson]
    }

    geometries.forEach((geom, index) => {
      let points = []
      if (geom.type === 'Polygon') {
        points = geom.coordinates[0].flat()
      } else if (geom.type === 'MultiPolygon') {
        points = geom.coordinates[0][0].flat()
      }

      if (points.length < 4) return

      // 样式区分：索引0是地板，其他是镂空
      const isFloor = index === 0

      const poly = new Konva.Line({
        points: points,
        closed: true,
        // 地板用浅灰，镂空用背景色覆盖(模拟挖空)
        fill: isFloor ? '#e2e8f0' : '#f8fafc',
        stroke: '#94a3b8', // 边框颜色
        strokeWidth: 2 / (stage ? stage.scaleX() : 1), // 这里的边框可以稍微粗一点
        listening: false, // 底图不响应点击事件，避免干扰上方区域的操作
        id: `base-${index}`
      })

      baseLayer.add(poly)
    })

    baseLayer.batchDraw()
  }

  // 绘制单个多边形区域 (店铺、活动区等)
  const drawPolygon = (area, type) => {
    if (!area.geometry || !area.geometry.coordinates) return

    let points = []
    if (area.geometry.type === 'Polygon') {
      points = area.geometry.coordinates[0].flat()
    } else if (area.geometry.type === 'MultiPolygon') {
      points = area.geometry.coordinates[0][0].flat()
    }

    if (points.length < 4) return

    const color = typeColors[type]

    const poly = new Konva.Line({
      points: points,
      closed: true,
      fill: `${color}33`,
      stroke: color,
      strokeWidth: 1 / (stage ? stage.scaleX() : 1),
      draggable: true,
      name: 'feature-shape',
      id: `${type}-${area.id}`,
      hitStrokeWidth: 10
    })

    if (selectedFeature.value?.id === area.id && selectedType.value === type) {
      poly.strokeWidth(3 / (stage ? stage.scaleX() : 1))
      poly.fill(`${color}66`)
      poly.shadowColor('black')
      poly.shadowBlur(10)
      poly.shadowOpacity(0.3)
      poly.moveToTop()
    }

    poly.on('click tap', (e) => {
      e.cancelBubble = true
      selectFeature(type, area)
    })

    poly.on('dragend', function() {
      handleGeometryUpdate(type, area, this)
    })

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

  // 绘制设施
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
    const radius = 5 / (stage ? stage.scaleX() : 1)

    const circle = new Konva.Circle({
      x, y,
      radius: Math.max(radius, 2),
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
      // 设施位置更新逻辑: 目前仅更新 UI 状态
      facility.location = { x: this.x(), y: this.y() }
      // 如果需要调用后端 API，需在 editor 模块补充 updateFacilityLocation 接口
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
    const points = shapeNode.points()
    const dx = shapeNode.x()
    const dy = shapeNode.y()

    const newCoords = []
    for (let i = 0; i < points.length; i += 2) {
      newCoords.push([points[i] + dx, points[i+1] + dy])
    }

    if (newCoords.length > 0) {
      const start = newCoords[0]
      const end = newCoords[newCoords.length - 1]
      if (start[0] !== end[0] || start[1] !== end[1]) {
        newCoords.push([...start])
      }
    }

    area.geometry = { type: 'Polygon', coordinates: [newCoords] }

    shapeNode.position({ x: 0, y: 0 })
    shapeNode.points(newCoords.flat())
    shapesLayer.batchDraw()

    console.log(`[Save] 更新 ${type} ID:${area.id} 几何数据`)

    // 调用 API 保存
    try {
      const apiMap = {
        storearea: managementAPI.updateManagementStorearea, // 注意：后端需确保 management 模块允许更新 shape，或者切换到 editor 模块的 API
        eventarea: managementAPI.updateManagementEventarea,
        otherarea: managementAPI.updateManagementOtherarea
      }
      // 根据你提供的 editor.js，应该使用 editor 模块的 API 来更新 shape
      // 这里如果 managementAPI 不允许更新 shape，请引入 editorAPI 并替换
      // 示例: editorAPI.updateEditorStoreareaShape(area.id, area.geometry)
    } catch (e) {
      console.error('保存失败', e)
    }
  }

  // --- 5. 初始化逻辑 ---
  const initKonva = () => {
    const container = stageContainerRef.value

    if (!container || !currentMap.value) return

    const width = container.clientWidth
    const height = container.clientHeight

    if (width === 0 || height === 0) return

    if (stage) stage.destroy()

    stage = new Konva.Stage({
      container,
      width,
      height,
      draggable: true
    })

    layer = new Konva.Layer()      // 最底层背景
    baseLayer = new Konva.Layer()  // 建筑轮廓
    shapesLayer = new Konva.Layer()// 业务图层

    // 1. 绘制无限大背景，接收拖拽和取消选中事件
    const bg = new Konva.Rect({
      x: -50000, y: -50000, width: 100000, height: 100000,
      fill: '#f8fafc' // 整个画布背景色
    })

    bg.on('click', () => {
      selectFeature('', null)
    })

    layer.add(bg)

    // 按顺序添加图层
    stage.add(layer)
    stage.add(baseLayer)
    stage.add(shapesLayer)

    // 滚轮缩放
    stage.on('wheel', (e) => {
      e.evt.preventDefault()
      const scaleBy = 1.1
      const oldScale = stage.scaleX()
      const pointer = stage.getPointerPosition()

      const mousePointTo = {
        x: (pointer.x - stage.x()) / oldScale,
        y: (pointer.y - stage.y()) / oldScale,
      }

      const direction = e.evt.deltaY > 0 ? -1 : 1
      const newScale = direction > 0 ? oldScale * scaleBy : oldScale / scaleBy

      stage.scale({ x: newScale, y: newScale })

      const newPos = {
        x: pointer.x - mousePointTo.x * newScale,
        y: pointer.y - mousePointTo.y * newScale,
      }
      stage.position(newPos)
    })

    // 绘制内容
    drawBaseMap()     // 绘制建筑底图
    drawAllFeatures() // 绘制业务区域

    autoFitView() // 自动适配
  }

  // --- 6. 响应式监听 ---
  watchPostEffect(() => {
    const isReady = currentMap.value && stageContainerRef.value && !loading.value

    if (isReady) {
      if (!stage || (stage && stage.attrs.mapId !== currentMap.value.id)) {
        initKonva()
        if (stage) stage.attrs.mapId = currentMap.value.id
      } else {
        // 数据更新时重绘（例如属性变更、选中切换）
        // 如果底图没变，可以只重绘 shapesLayer，但这里为了简单全重绘
        drawBaseMap()
        drawAllFeatures()
      }
    }
  })

  onUnmounted(() => {
    if (stage) stage.destroy()
  })

  return {
    autoFitView
  }
}
