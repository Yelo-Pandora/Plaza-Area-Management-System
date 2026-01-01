import { watchPostEffect, onUnmounted, nextTick } from 'vue'
import { useMapEditorStore } from '../../composables/useMapEditorStore'
import * as managementAPI from '@/api/management'
import * as KonvaImport from 'konva'

// --- 引入 SVG 图标 ---
import escalatorIcon from '@/assets/icons/escalator.svg'
import fireExtinguisherIcon from '@/assets/icons/fire_extinguisher.svg'
import exitIcon from '@/assets/icons/exit.svg'
import infoIcon from '@/assets/icons/info.svg'
import otherIcon from '@/assets/icons/other.svg'

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

// --- 配置常量 ---
const LABEL_VISIBLE_THRESHOLD = 1.2
const MIN_VISIBLE_FONT_SIZE = 10
const ICON_BASE_RADIUS = 12

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
  let baseLayer = null
  let shapesLayer = null

  const typeColors = {
    storearea: '#2563eb',
    eventarea: '#16a34a',
    otherarea: '#f97316',
  }

  // --- 图片资源管理 ---
  const iconImages = {}
  const iconSources = {
    0: escalatorIcon,
    1: fireExtinguisherIcon,
    2: exitIcon,
    3: infoIcon,
    4: otherIcon
  }

  const loadIcons = () => {
    const promises = Object.keys(iconSources).map(type => {
      return new Promise((resolve) => {
        const img = new Image()
        img.src = iconSources[type]
        img.onload = () => {
          iconImages[type] = img
          resolve()
        }
        img.onerror = () => {
          console.warn(`Failed to load icon for type ${type}`)
          resolve()
        }
      })
    })
    Promise.all(promises).then(() => {
      if (shapesLayer) shapesLayer.batchDraw()
    })
  }

  loadIcons()

  const facilityStyles = {
    0: { color: '#3b82f6' },
    1: { color: '#ec4899' },
    2: { color: '#10b981' },
    3: { color: '#f59e0b' },
    4: { color: '#8b5cf6' }
  }

  // --- 辅助函数 ---
  const getAreaName = (area, type) => {
    if (type === 'storearea') return area.store_name || '未命名店铺'
    if (type === 'eventarea') {
      const types = { 0: '普通活动区域', 1: '促销活动', 2: '展览活动', 3: '表演活动' }
      return types[area.type] !== undefined ? types[area.type] : '活动区域'
    }
    if (type === 'otherarea') {
      const types = { 0: '公共区域', 1: '办公区域', 2: '设备区域', 3: '其他区域' }
      return types[area.type] !== undefined ? types[area.type] : '其他区域'
    }
    if (type === 'facility') return area.description || '设施'
    return ''
  }

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

  // --- 视图更新逻辑 ---

  const updateLabelVisibility = (scale) => {
    if (!shapesLayer) return

    // 查找所有的文字节点 (修正为查找 .area-label 而不是 .text-group)
    const labels = shapesLayer.find('.area-label')
    let hasChange = false

    labels.forEach(label => {
      const mapFontSize = label.fontSize()
      const screenFontSize = mapFontSize * scale

      const shouldVisible = screenFontSize >= MIN_VISIBLE_FONT_SIZE

      if (label.visible() !== shouldVisible) {
        label.visible(shouldVisible)
        hasChange = true
      }
    })

    if (hasChange) {
      shapesLayer.batchDraw()
    }
  }

  const updateIconsScale = (stageScale) => {
    if (!shapesLayer) return
    const groups = shapesLayer.find('.facility-group')
    const invScale = 1 / stageScale

    groups.forEach(group => {
      group.scale({ x: invScale, y: invScale })
    })
  }

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

    updateLabelVisibility(scale)
    updateIconsScale(scale)

    stage.batchDraw()
  }

  // --- 绘制逻辑 ---

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

  // 绘制多边形区域 (移除裁剪逻辑，直接绘制文字)
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
    const bounds = getBoundingBox(absolutePoints)

    // 1. 主组
    const mainGroup = new Konva.Group({
      x: bounds.centerX,
      y: bounds.centerY,
      draggable: true,
      id: `${type}-${area.id}`
    })

    const relativePoints = []
    for (let i = 0; i < absolutePoints.length; i += 2) {
      relativePoints.push(absolutePoints[i] - bounds.centerX)
      relativePoints.push(absolutePoints[i+1] - bounds.centerY)
    }

    const currentScale = stage ? stage.scaleX() : 1

    // 2. 多边形形状
    const poly = new Konva.Line({
      points: relativePoints,
      closed: true,
      fill: isSelected ? `${color}66` : `${color}33`,
      stroke: color,
      strokeWidth: (isSelected ? 3 : 1) / currentScale,
      shadowColor: 'black',
      shadowBlur: isSelected ? 10 : 0,
      shadowOpacity: 0.3,
      hitStrokeWidth: 10,
      name: 'feature-shape'
    })

    mainGroup.add(poly)

    const areaName = getAreaName(area, type)

    // 计算字号：/8 比例
    const fontSize = Math.min(bounds.width, bounds.height) / 8
    const initialVisible = (fontSize * currentScale) >= MIN_VISIBLE_FONT_SIZE

    // 3. 文字 (直接添加到主组，不再使用裁剪组)
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
      wrap: 'word',    // 自动换行
      ellipsis: false, // 禁用省略号，显示完整内容
      padding: 2,      // 稍微减小内边距
      listening: false,
      name: 'area-label', // 标记为标签
      visible: initialVisible
    })
    // 抵消缩放
    text.scale({ x: 1, y: 1 })

    mainGroup.add(text)

    // 事件处理
    mainGroup.on('click tap', (e) => {
      e.cancelBubble = true
      selectFeature(type, area)
    })

    mainGroup.on('dragend', function() {
      handleGroupDragEnd(type, area, this, relativePoints)
    })

    mainGroup.on('mouseenter', () => {
      stage.container().style.cursor = 'pointer'
      if (!isSelected) {
        poly.fill(`${color}55`)
        shapesLayer.batchDraw()
      }
    })

    mainGroup.on('mouseleave', () => {
      stage.container().style.cursor = 'default'
      if (!isSelected) {
        poly.fill(`${color}33`)
        shapesLayer.batchDraw()
      }
    })

    if (isSelected) {
      mainGroup.moveToTop()
    }

    shapesLayer.add(mainGroup)
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

    const type = (facility.type !== undefined && facility.type !== null) ? facility.type : 4
    const style = facilityStyles[type] || facilityStyles[4]
    const isSelected = selectedFeature.value?.id === facility.id && selectedType.value === 'facility'

    const currentStageScale = stage ? stage.scaleX() : 1
    const invScale = 1 / currentStageScale

    const group = new Konva.Group({
      x: x,
      y: y,
      draggable: true,
      id: `facility-${facility.id}`,
      name: 'facility-group',
      scaleX: invScale,
      scaleY: invScale
    })

    const circle = new Konva.Circle({
      x: 0,
      y: 0,
      radius: ICON_BASE_RADIUS,
      fill: style.color,
      stroke: isSelected ? 'yellow' : 'white',
      strokeWidth: isSelected ? 3 : 1,
      shadowColor: 'black',
      shadowBlur: isSelected ? 10 : 0,
      shadowOpacity: 0.3
    })

    group.add(circle)

    const imgObj = iconImages[type]
    if (imgObj) {
      const iconSize = ICON_BASE_RADIUS * 1.4
      const icon = new Konva.Image({
        image: imgObj,
        width: iconSize,
        height: iconSize,
        x: -iconSize / 2,
        y: -iconSize / 2,
        listening: false
      })
      group.add(icon)
    }

    group.on('click tap', (e) => {
      e.cancelBubble = true
      selectFeature('facility', facility)
    })

    group.on('mouseenter', () => {
      stage.container().style.cursor = 'pointer'
    })

    group.on('mouseleave', () => {
      stage.container().style.cursor = 'default'
    })

    group.on('dragend', function() {
      facility.location = { x: this.x(), y: this.y() }
    })

    if (isSelected) {
      group.moveToTop()
    }

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

  const handleGroupDragEnd = async (type, area, groupNode, relativePoints) => {
    const centerX = groupNode.x()
    const centerY = groupNode.y()

    const newCoords = []
    for (let i = 0; i < relativePoints.length; i += 2) {
      newCoords.push([
        relativePoints[i] + centerX,
        relativePoints[i+1] + centerY
      ])
    }

    if (newCoords.length > 0) {
      const start = newCoords[0]
      const end = newCoords[newCoords.length - 1]
      if (start[0] !== end[0] || start[1] !== end[1]) {
        newCoords.push([...start])
      }
    }

    area.geometry = { type: 'Polygon', coordinates: [newCoords] }
  }

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

    // 缩放事件监听
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

      stage.batchDraw()

      // 延迟更新文字显隐，避免缩放时闪烁
      nextTick(() => {
         updateLabelVisibility(newScale)
         updateIconsScale(newScale)
      })
    })

    drawBaseMap()
    drawAllFeatures()
    autoFitView()
  }

  // --- 6. 响应式监听 ---
  watchPostEffect(() => {
    const isReady = currentMap.value && stageContainerRef.value && !loading.value
    if (isReady) {
      const isStageValid = stage && stage.container() === stageContainerRef.value

      if (!isStageValid || stage.attrs.mapId !== currentMap.value.id) {
        initKonva()
        if (stage) stage.attrs.mapId = currentMap.value.id
      } else {
        drawBaseMap()
        drawAllFeatures()
        if (stage) {
          const s = stage.scaleX()
          updateLabelVisibility(s)
          updateIconsScale(s)
        }
      }
    }
  })

  onUnmounted(() => {
    if (stage) stage.destroy()
  })

  return { autoFitView }
}
