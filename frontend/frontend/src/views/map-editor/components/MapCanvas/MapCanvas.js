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
  let layer = null       // 背景层
  let baseLayer = null   // 底图层
  let shapesLayer = null // 业务层

  const typeColors = {
    storearea: '#2563eb',
    eventarea: '#16a34a',
    otherarea: '#f97316',
    facility: '#8b5cf6',
  }

  // --- 辅助：获取区域名称 ---
  const getAreaName = (area, type) => {
    if (type === 'storearea') return area.store_name || '未命名店铺'

    // 修改：Eventarea 显示类型名称
    if (type === 'eventarea') {
      const types = { 0: '普通活动区域', 1: '促销活动', 2: '展览活动', 3: '表演活动' }
      // 注意：area.type 可能是 0，所以不能简单的 ||
      return types[area.type] !== undefined ? types[area.type] : '活动区域'
    }

    // 修改：Otherarea 显示类型名称
    if (type === 'otherarea') {
      const types = { 0: '公共区域', 1: '办公区域', 2: '设备区域', 3: '其他' }
      return types[area.type] !== undefined ? types[area.type] : '其他区域'
    }

    if (type === 'facility') return area.description || '设施'
    return ''
  }

  // --- 辅助：计算多边形包围盒 ---
  const getBoundingBox = (points) => {
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
    for (let i = 0; i < points.length; i += 2) {
      const x = points[i]
      const y = points[i+1]
      minX = Math.min(minX, x)
      maxX = Math.max(maxX, x)
      minY = Math.min(minY, y)
      maxY = Math.max(maxY, y)
    }
    return {
      x: minX,
      y: minY,
      width: maxX - minX,
      height: maxY - minY,
      centerX: minX + (maxX - minX) / 2,
      centerY: minY + (maxY - minY) / 2
    }
  }

  // --- 2. 自动适配视图 ---
  const autoFitView = () => {
    const targetLayer = (baseLayer && baseLayer.hasChildren()) ? baseLayer : shapesLayer
    if (!stage || !targetLayer) return

    const box = targetLayer.getClientRect({ skipTransform: true })
    if (box.width === 0 || box.height === 0) {
      stage.position({ x: 0, y: 0 })
      stage.scale({ x: 1, y: 1 })
      return
    }

    const padding = 50
    const stageWidth = stage.width()
    const stageHeight = stage.height()

    const scaleX = (stageWidth - padding * 2) / box.width
    const scaleY = (stageHeight - padding * 2) / box.height
    const scale = Math.min(scaleX, scaleY)

    const centerX = stageWidth / 2 - (box.x + box.width / 2) * scale
    const centerY = stageHeight / 2 - (box.y + box.height / 2) * scale

    stage.position({ x: centerX, y: centerY })
    stage.scale({ x: scale, y: scale })
    stage.batchDraw()
  }

  // --- 3. 绘制逻辑 ---

  const drawBaseMap = () => {
    if (!baseLayer || !currentMap.value || !currentMap.value.detail_geojson) return
    baseLayer.destroyChildren()

    const geojson = currentMap.value.detail_geojson
    let geometries = []
    if (geojson.type === 'GeometryCollection') {
      geometries = geojson.geometries
    } else if (geojson.type === 'Polygon' || geojson.type === 'MultiPolygon') {
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

      const isFloor = index === 0
      const poly = new Konva.Line({
        points: points,
        closed: true,
        fill: isFloor ? '#e2e8f0' : '#f8fafc',
        stroke: '#94a3b8',
        strokeWidth: 2 / (stage ? stage.scaleX() : 1),
        listening: false,
        id: `base-${index}`
      })
      baseLayer.add(poly)
    })
    baseLayer.batchDraw()
  }

  // 绘制多边形区域 (带文字)
  const drawPolygon = (area, type) => {
    if (!area.geometry || !area.geometry.coordinates) return

    let absolutePoints = []
    if (area.geometry.type === 'Polygon') {
      absolutePoints = area.geometry.coordinates[0].flat()
    } else if (area.geometry.type === 'MultiPolygon') {
      absolutePoints = area.geometry.coordinates[0][0].flat()
    }

    if (absolutePoints.length < 4) return

    const color = typeColors[type]
    const isSelected = selectedFeature.value?.id === area.id && selectedType.value === type

    // 1. 计算包围盒和中心点
    const bounds = getBoundingBox(absolutePoints)

    // 2. 创建 Group，位置设为几何中心
    const group = new Konva.Group({
      x: bounds.centerX,
      y: bounds.centerY,
      draggable: true,
      id: `${type}-${area.id}`
    })

    // 3. 将绝对坐标转换为相对于 Group 中心 (0,0) 的相对坐标
    const relativePoints = []
    for (let i = 0; i < absolutePoints.length; i += 2) {
      relativePoints.push(absolutePoints[i] - bounds.centerX)
      relativePoints.push(absolutePoints[i+1] - bounds.centerY)
    }

    // 4. 创建图形 (Polygon)
    const poly = new Konva.Line({
      points: relativePoints,
      closed: true,
      fill: isSelected ? `${color}66` : `${color}33`,
      stroke: color,
      strokeWidth: (isSelected ? 3 : 1) / (stage ? stage.scaleX() : 1),
      shadowColor: 'black',
      shadowBlur: isSelected ? 10 : 0,
      shadowOpacity: 0.3,
      hitStrokeWidth: 10,
      name: 'feature-shape'
    })

    // 5. 创建文字 (Text)
    const areaName = getAreaName(area, type)

    // 根据包围盒大小计算字体，确保能放入框内
    const fontSize = Math.min(bounds.width, bounds.height) / 4

    const text = new Konva.Text({
      x: -bounds.width / 2,
      y: -bounds.height / 2,
      width: bounds.width,
      height: bounds.height,
      text: areaName,
      fontSize: fontSize,
      fontFamily: 'sans-serif',
      fill: '#1e293b',
      align: 'center',
      verticalAlign: 'middle',
      ellipsis: true,
      wrap: 'none',
      listening: false,
    })

    text.scale({ x: 1, y: 1 })

    // 6. 组装
    group.add(poly)
    group.add(text)

    // 7. 事件绑定
    group.on('click tap', (e) => {
      e.cancelBubble = true
      selectFeature(type, area)
    })

    group.on('dragend', function() {
      handleGroupDragEnd(type, area, this, relativePoints)
    })

    group.on('mouseenter', () => {
      stage.container().style.cursor = 'pointer'
      if (!isSelected) {
        poly.fill(`${color}55`)
        shapesLayer.batchDraw()
      }
    })

    group.on('mouseleave', () => {
      stage.container().style.cursor = 'default'
      if (!isSelected) {
        poly.fill(`${color}33`)
        shapesLayer.batchDraw()
      }
    })

    if (isSelected) {
      group.moveToTop()
    }

    shapesLayer.add(group)
  }

  // 绘制设施 (点/圆)
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
    const isSelected = selectedFeature.value?.id === facility.id && selectedType.value === 'facility'

    const group = new Konva.Group({
      x: x,
      y: y,
      draggable: true,
      id: `facility-${facility.id}`
    })

    const circle = new Konva.Circle({
      x: 0,
      y: 0,
      radius: Math.max(radius, 2),
      fill: color,
      stroke: isSelected ? 'yellow' : 'white',
      strokeWidth: isSelected ? 2 : 1,
      shadowBlur: isSelected ? 5 : 0
    })

    // 设施文字已移除

    group.add(circle)

    group.on('click tap', (e) => {
      e.cancelBubble = true
      selectFeature('facility', facility)
    })

    group.on('dragend', function() {
      facility.location = { x: this.x(), y: this.y() }
      console.log(`[Save] 设施移动到: ${this.x()}, ${this.y()}`)
    })

    shapesLayer.add(group)
  }

  const drawAllFeatures = () => {
    if (!shapesLayer) return
    shapesLayer.destroyChildren()

    storeareas.value.forEach(a => drawPolygon(a, 'storearea'))
    eventareas.value.forEach(a => drawPolygon(a, 'eventarea'))
    otherareas.value.forEach(a => drawPolygon(a, 'otherarea'))
    facilities.value.forEach(f => drawFacility(f))

    shapesLayer.batchDraw()
  }

  // --- 4. 数据保存逻辑 (适配 Group 模式) ---
  const handleGroupDragEnd = async (type, area, groupNode, relativePoints) => {
    // 获取 Group 移动后的新中心点绝对坐标
    const centerX = groupNode.x()
    const centerY = groupNode.y()

    // 还原回绝对坐标数组
    const newCoords = []
    for (let i = 0; i < relativePoints.length; i += 2) {
      newCoords.push([
        relativePoints[i] + centerX,
        relativePoints[i+1] + centerY
      ])
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

    console.log(`[Save] 更新 ${type} ID:${area.id} 几何数据`)

    // 调用 API 保存
    try {
      const apiMap = {
        storearea: managementAPI.updateManagementStorearea,
        eventarea: managementAPI.updateManagementEventarea,
        otherarea: managementAPI.updateManagementOtherarea
      }
      // 实际项目中需替换为 editorAPI.updateShape 等允许更新几何的接口
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

    layer = new Konva.Layer()
    baseLayer = new Konva.Layer()
    shapesLayer = new Konva.Layer()

    const bg = new Konva.Rect({
      x: -50000, y: -50000, width: 100000, height: 100000,
      fill: '#f8fafc'
    })

    bg.on('click', () => {
      selectFeature('', null)
    })

    layer.add(bg)
    stage.add(layer)
    stage.add(baseLayer)
    stage.add(shapesLayer)

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

    drawBaseMap()
    drawAllFeatures()
    autoFitView()
  }

  watchPostEffect(() => {
    const isReady = currentMap.value && stageContainerRef.value && !loading.value
    if (isReady) {
      const isStageValid = stage && stage.container() === stageContainerRef.value

      if (!isStageValid || stage.attrs.mapId !== currentMap.value.id){
        initKonva()
        if (stage) stage.attrs.mapId = currentMap.value.id
      } else {
        drawBaseMap()
        drawAllFeatures()
      }
    }
  })

  onUnmounted(() => {
    if (stage) stage.destroy()
  })

  return { autoFitView }
}
