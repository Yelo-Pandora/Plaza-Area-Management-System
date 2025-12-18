<!-- views/map-editor/index.vue -->
<template>
  <div class="map-editor">
    <!-- 头部区域 -->
    <div class="header">
      <h1 class="title">地图编辑器</h1>
      <div class="actions">
        <div class="map-selector">
          <select v-model="currentMapId" @change="handleMapChange" class="filter-select">
            <option value="">选择地图</option>
            <option v-for="m in maps" :key="m.id" :value="m.id">
              {{ m.building_name || '地图' }} - 楼层 {{ m.floor_number }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- 主体内容：三层布局 -->
    <div class="map-editor-body">
      <!-- 左侧：图层列表 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h3 class="sidebar-title">区域列表</h3>
          <button class="btn btn-primary" @click="showCreateModal = true">
            <span class="btn-icon">+</span> 新建区域
          </button>
        </div>

        <div class="layer-groups">
          <!-- 店铺区域图层 -->
          <div class="layer-group">
            <div class="layer-group-header" @click="toggleLayer('storearea')">
              <span class="layer-icon">🏪</span>
              <span class="layer-title">店铺区域</span>
              <span class="layer-count">({{ storeareas.length }})</span>
              <span :class="['layer-toggle', { expanded: expandedLayers.storearea }]">
                {{ expandedLayers.storearea ? '▼' : '▶' }}
              </span>
            </div>
            <div v-if="expandedLayers.storearea" class="layer-items">
              <div
                v-for="area in storeareas"
                :key="area.id"
                :class="['layer-item', { selected: selectedFeature?.id === area.id && selectedType === 'storearea' }]"
                @click="selectFeature('storearea', area)"
              >
                <span class="layer-item-name">{{ area.store_name || '未命名' }}</span>
              </div>
            </div>
          </div>

          <!-- 活动区域图层 -->
          <div class="layer-group">
            <div class="layer-group-header" @click="toggleLayer('eventarea')">
              <span class="layer-icon">🎪</span>
              <span class="layer-title">活动区域</span>
              <span class="layer-count">({{ eventareas.length }})</span>
              <span :class="['layer-toggle', { expanded: expandedLayers.eventarea }]">
                {{ expandedLayers.eventarea ? '▼' : '▶' }}
              </span>
            </div>
            <div v-if="expandedLayers.eventarea" class="layer-items">
              <div
                v-for="area in eventareas"
                :key="area.id"
                :class="['layer-item', { selected: selectedFeature?.id === area.id && selectedType === 'eventarea' }]"
                @click="selectFeature('eventarea', area)"
              >
                <span class="layer-item-name">{{ area.event_name || '未命名' }}</span>
              </div>
            </div>
          </div>

          <!-- 其他区域图层 -->
          <div class="layer-group">
            <div class="layer-group-header" @click="toggleLayer('otherarea')">
              <span class="layer-icon">🏢</span>
              <span class="layer-title">其他区域</span>
              <span class="layer-count">({{ otherareas.length }})</span>
              <span :class="['layer-toggle', { expanded: expandedLayers.otherarea }]">
                {{ expandedLayers.otherarea ? '▼' : '▶' }}
              </span>
            </div>
            <div v-if="expandedLayers.otherarea" class="layer-items">
              <div
                v-for="area in otherareas"
                :key="area.id"
                :class="['layer-item', { selected: selectedFeature?.id === area.id && selectedType === 'otherarea' }]"
                @click="selectFeature('otherarea', area)"
              >
                <span class="layer-item-name">{{ area.name || '未命名' }}</span>
              </div>
            </div>
          </div>

          <!-- 设施图层 -->
          <div class="layer-group">
            <div class="layer-group-header" @click="toggleLayer('facility')">
              <span class="layer-icon">�</span>
              <span class="layer-title">设施</span>
              <span class="layer-count">({{ facilities.length }})</span>
              <span :class="['layer-toggle', { expanded: expandedLayers.facility }]">
                {{ expandedLayers.facility ? '▼' : '▶' }}
              </span>
            </div>
            <div v-if="expandedLayers.facility" class="layer-items">
              <div
                v-for="facility in facilities"
                :key="facility.id"
                :class="['layer-item', { selected: selectedFeature?.id === facility.id && selectedType === 'facility' }]"
                @click="selectFeature('facility', facility)"
              >
                <span class="layer-item-name">{{ facility.description || '未命名' }}</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 中间：地图画布 -->
      <main class="map-canvas-container">
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <span>加载中...</span>
        </div>

        <div v-else-if="!currentMap" class="empty-state">
          <span class="empty-icon">🗺️</span>
          <p>请选择一个地图进行编辑</p>
        </div>

        <div v-else class="map-canvas-wrapper">
          <div ref="stageContainer" class="konva-stage-container"></div>
        </div>
      </main>

      <!-- 右侧：属性面板 -->
      <aside class="properties-panel">
        <div class="panel-header">
          <h3 class="panel-title">属性编辑</h3>
        </div>

        <div v-if="!selectedFeature" class="panel-empty">
          <p>请选择一个区域进行编辑</p>
        </div>

        <div v-else class="panel-content">
          <form @submit.prevent="saveAttributes" class="properties-form">
            <div v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </div>

            <div class="form-group">
              <label class="form-label">ID</label>
              <input type="text" :value="selectedFeature.id" class="form-input" disabled>
            </div>

            <div class="form-group">
              <label class="form-label">名称</label>
              <input
                v-model="form.name"
                type="text"
                class="form-input"
                :placeholder="`请输入${getTypeName()}名称`"
              >
            </div>

            <div class="form-group">
              <label class="form-label">类型</label>
              <select v-model="form.type" class="form-select">
                <option v-if="selectedType === 'storearea'" value="0">普通店铺</option>
                <option v-if="selectedType === 'storearea'" value="1">餐饮</option>
                <option v-if="selectedType === 'storearea'" value="2">服饰</option>
                <option v-if="selectedType === 'storearea'" value="3">娱乐</option>
                <option v-if="selectedType === 'storearea'" value="4">服务</option>
                <option v-if="selectedType === 'eventarea'" value="0">普通活动区域</option>
                <option v-if="selectedType === 'eventarea'" value="1">促销活动</option>
                <option v-if="selectedType === 'eventarea'" value="2">展览活动</option>
                <option v-if="selectedType === 'eventarea'" value="3">表演活动</option>
                <option v-if="selectedType === 'otherarea'" value="0">公共区域</option>
                <option v-if="selectedType === 'otherarea'" value="1">办公区域</option>
                <option v-if="selectedType === 'otherarea'" value="2">设备区域</option>
                <option v-if="selectedType === 'otherarea'" value="3">其他</option>
                <option v-if="selectedType === 'facility'" value="0">电梯</option>
                <option v-if="selectedType === 'facility'" value="1">卫生间</option>
                <option v-if="selectedType === 'facility'" value="2">安全出口</option>
                <option v-if="selectedType === 'facility'" value="3">服务台</option>
                <option v-if="selectedType === 'facility'" value="4">其他</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">描述</label>
              <textarea
                v-model="form.description"
                class="form-textarea"
                rows="3"
                :placeholder="`请输入${getTypeName()}描述`"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">状态</label>
              <div class="toggle-switch">
                <input
                  v-model="form.is_active"
                  type="checkbox"
                  id="status-toggle"
                  class="toggle-input"
                >
                <label for="status-toggle" class="toggle-label">
                  <span class="toggle-slider"></span>
                  <span class="toggle-text">{{ form.is_active ? '启用' : '停用' }}</span>
                </label>
              </div>
            </div>

            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting" class="btn-spinner"></span>
                保存
              </button>
            </div>
          </form>
        </div>
      </aside>
    </div>

    <!-- 新建区域弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">新建区域</h3>
          <button class="modal-close" @click="closeCreateModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleCreateArea">
            <div v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </div>

            <div class="form-group">
              <label class="form-label">区域类型</label>
              <select v-model="createForm.type" class="form-select">
                <option value="storearea">店铺区域</option>
                <option value="eventarea">活动区域</option>
                <option value="otherarea">其他区域</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">图形模板</label>
              <div class="shape-templates">
                <div
                  v-for="tpl in shapeTemplates"
                  :key="tpl.shape"
                  :class="['shape-template', { selected: createForm.shape === tpl.shape }]"
                  @click="createForm.shape = tpl.shape"
                >
                  <span class="template-icon">{{ tpl.icon }}</span>
                  <span class="template-label">{{ tpl.label }}</span>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">大小</label>
              <div class="size-control">
                <input
                  v-model.number="createForm.size"
                  type="range"
                  min="10"
                  max="50"
                  class="size-slider"
                >
                <span class="size-value">{{ createForm.size }}</span>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="closeCreateModal" :disabled="submitting">
                取消
              </button>
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting" class="btn-spinner"></span>
                创建
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { listMaps, getMapById } from '../../api/map'
import * as managementAPI from '../../api/management'

// 地图数据
const maps = ref([])
const currentMapId = ref('')
const currentMap = ref(null)
const loading = ref(false)
const errorMessage = ref('')

// 图层数据
const storeareas = ref([])
const eventareas = ref([])
const otherareas = ref([])
const facilities = ref([])

// 选择状态
const selectedType = ref('')
const selectedFeature = ref(null)

// 图层展开状态
const expandedLayers = reactive({
  storearea: true,
  eventarea: true,
  otherarea: true,
  facility: true
})

// 新建区域表单
const showCreateModal = ref(false)
const submitting = ref(false)
const createForm = reactive({
  type: 'storearea',
  shape: 'square',
  size: 20
})

// 属性编辑表单
const form = reactive({
  id: null,
  name: '',
  type: '',
  description: '',
  is_active: true
})

// Konva 相关
const stageContainer = ref(null)
let stage = null
let layer = null
let shapesLayer = null

// 形状模板
const shapeTemplates = [
  { label: '正方形', shape: 'square', icon: '◼️', defaultSize: 20 },
  { label: '矩形', shape: 'rect', icon: '▭️', defaultSize: 30 },
  { label: '圆形', shape: 'circle', icon: '⭕', defaultSize: 24 },
  { label: '三角形', shape: 'triangle', icon: '🔺', defaultSize: 24 },
  { label: '六边形', shape: 'hexagon', icon: '⬢', defaultSize: 20 }
]

// 类型名称映射
const typeNames = {
  storearea: '店铺',
  eventarea: '活动区域',
  otherarea: '其他区域',
  facility: '设施'
}

// 类型颜色映射
const typeColors = {
  storearea: '#2563eb',
  eventarea: '#16a34a',
  otherarea: '#f97316',
  facility: '#8b5cf6'
}

// 获取类型名称
const getTypeName = () => {
  return typeNames[selectedType.value] || '区域'
}

// 切换图层展开状态
const toggleLayer = (layerType) => {
  expandedLayers[layerType] = !expandedLayers[layerType]
}

// 选择要素
const selectFeature = (type, feature) => {
  selectedType.value = type
  selectedFeature.value = feature
  
  // 填充表单数据
  form.id = feature.id
  form.name = feature.name || feature.store_name || feature.event_name || feature.description || ''
  form.type = feature.store_type?.toString() || feature.event_type?.toString() || feature.type?.toString() || '0'
  form.description = feature.description || ''
  form.is_active = feature.is_active !== undefined ? feature.is_active : true
  
  // 重新绘制以显示选中状态
  drawAreas()
}

// 加载地图列表
const loadMaps = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const response = await listMaps()
    maps.value = response.data || response
    
    if (maps.value.length > 0 && !currentMapId.value) {
      currentMapId.value = maps.value[0].id
      await loadCurrentMap()
    }
  } catch (error) {
    console.error('加载地图列表失败:', error)
    errorMessage.value = `加载地图列表失败: ${error.message || '未知错误'}`
  } finally {
    loading.value = false
  }
}

// 处理地图切换
const handleMapChange = async () => {
  if (!currentMapId.value) {
    currentMap.value = null
    return
  }
  await loadCurrentMap()
}

// 加载当前地图
const loadCurrentMap = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const response = await getMapById(currentMapId.value)
    const mapData = response.data || response
    currentMap.value = mapData
    
    // 首先从地图数据中获取可能包含的区域和设施数据（如果后端API支持）
    let mapStoreareas = []
    let mapEventareas = []
    let mapOtherareas = []
    let mapFacilities = []
    
    // 检查地图数据中是否包含区域和设施信息
    if (mapData.stores) {
      mapStoreareas = mapData.stores
    } else if (mapData.storeareas) {
      mapStoreareas = mapData.storeareas
    }
    if (mapData.events) {
      mapEventareas = mapData.events
    } else if (mapData.eventareas) {
      mapEventareas = mapData.eventareas
    }
    if (mapData.other_areas) {
      mapOtherareas = mapData.other_areas
    } else if (mapData.otherareas) {
      mapOtherareas = mapData.otherareas
    }
    if (mapData.facilities) {
      mapFacilities = mapData.facilities
    }
    
    // 使用API获取所有区域数据（确保获取完整的非几何属性）
    const [storeareasData, eventareasData, otherareasData, facilitiesData] = await Promise.all([
      managementAPI.listManagementStoreareas(),
      managementAPI.listManagementEventareas(),
      managementAPI.listManagementOtherareas(),
      managementAPI.listManagementFacilities()
    ])
    
    // 过滤出当前地图的元素
    const mapId = currentMapId.value
    const mgmtStoreareas = (storeareasData.data || storeareasData).filter(area => area.map_id == mapId)
    const mgmtEventareas = (eventareasData.data || eventareasData).filter(area => area.map_id == mapId)
    const mgmtOtherareas = (otherareasData.data || otherareasData).filter(area => area.map_id == mapId)
    const mgmtFacilities = (facilitiesData.data || facilitiesData).filter(facility => facility.map_id == mapId)
    
    // 调试：检查API返回的数据结构
    console.log('地图数据中的店铺区域:', mapStoreareas)
    console.log('地图数据中的活动区域:', mapEventareas)
    console.log('地图数据中的其他区域:', mapOtherareas)
    console.log('地图数据中的设施:', mapFacilities)
    console.log('管理API中的店铺区域:', mgmtStoreareas)
    console.log('管理API中的活动区域:', mgmtEventareas)
    console.log('管理API中的其他区域:', mgmtOtherareas)
    console.log('管理API中的设施:', mgmtFacilities)
    
    // 合并数据：使用地图数据中的几何信息，管理API中的非几何属性
    storeareas.value = mergeAreaData(mapStoreareas, mgmtStoreareas, mapId)
    eventareas.value = mergeAreaData(mapEventareas, mgmtEventareas, mapId)
    otherareas.value = mergeAreaData(mapOtherareas, mgmtOtherareas, mapId)
    facilities.value = mergeFacilityData(mapFacilities, mgmtFacilities, mapId)
    
    // 调试：检查过滤后的数据
    console.log('过滤后店铺区域:', storeareas.value)
    console.log('过滤后活动区域:', eventareas.value)
    console.log('过滤后其他区域:', otherareas.value)
    console.log('过滤后设施:', facilities.value)
    
    // 清空选择
    selectedFeature.value = null
    selectedType.value = ''
    
    // 初始化 Konva 舞台
    await nextTick()
    await initKonva()
  } catch (error) {
    console.error('加载地图数据失败:', error)
    errorMessage.value = `加载地图数据失败: ${error.message || '未知错误'}`
  } finally {
    loading.value = false
  }
}

// 初始化 Konva
const initKonva = async () => {
  if (!stageContainer.value || !currentMap.value) return
  
  // 清除现有舞台
  if (stage) {
    stage.destroy()
  }
  
  // 创建 Konva 实例
  const Konva = await import('konva')
  
  // 创建舞台
  const containerWidth = stageContainer.value.offsetWidth
  const containerHeight = stageContainer.value.offsetHeight
  
  stage = new Konva.Stage({
    container: stageContainer.value,
    width: containerWidth,
    height: containerHeight,
    draggable: true
  })
  
  // 创建图层
  layer = new Konva.Layer()
  shapesLayer = new Konva.Layer()
  
  stage.add(layer)
  stage.add(shapesLayer)
  
  // 绘制地图和区域
  drawMap()
  drawAreas()
  
  // 添加事件监听
  addStageEvents(Konva)
}

// 绘制地图背景
const drawMap = () => {
  if (!layer) return
  
  // 清空图层
  layer.destroyChildren()
  
  // 绘制背景
  const background = new Konva.Rect({
    x: 0,
    y: 0,
    width: stage.width(),
    height: stage.height(),
    fill: '#f5f5f5',
    stroke: '#ddd',
    strokeWidth: 1
  })
  
  layer.add(background)
  layer.draw()
}

// 绘制所有区域
const drawAreas = () => {
  if (!shapesLayer) return
  
  // 清空现有图形
  shapesLayer.destroyChildren()
  
  // 绘制店铺区域
  storeareas.value.forEach(area => drawArea(area, 'storearea'))
  
  // 绘制活动区域
  eventareas.value.forEach(area => drawArea(area, 'eventarea'))
  
  // 绘制其他区域
  otherareas.value.forEach(area => drawArea(area, 'otherarea'))
  
  // 绘制设施
  facilities.value.forEach(facility => drawFacility(facility))
  
  shapesLayer.draw()
}

// 绘制单个区域
const drawArea = (area, type) => {
  if (!area.geometry || !area.geometry.coordinates || !shapesLayer) return
  
  // 设置颜色
  const color = typeColors[type]
  
  // 确保坐标数据格式正确
  let points = []
  if (area.geometry.type === 'Polygon') {
    // 处理多边形
    if (Array.isArray(area.geometry.coordinates[0])) {
      points = area.geometry.coordinates[0].flat()
    }
  } else if (area.geometry.type === 'MultiPolygon') {
    // 处理多多边形（取第一个多边形）
    if (Array.isArray(area.geometry.coordinates[0][0])) {
      points = area.geometry.coordinates[0][0].flat()
    }
  }
  
  if (points.length < 6) return // 至少需要3个点
  
  // 创建图形
  const polygon = new Konva.Polygon({
    points: points,
    closed: true,
    fill: `${color}30`,
    stroke: color,
    strokeWidth: 1,
    draggable: true,
    id: `${type}-${area.id}`
  })
  
  // 选中状态
  if (selectedFeature.value?.id === area.id && selectedType.value === type) {
    polygon.strokeWidth(2)
    polygon.fill(`${color}40`)
    polygon.shadowBlur(5)
    polygon.shadowColor(color)
  }
  
  // 绑定事件
  polygon.on('click', () => selectFeature(type, area))
  polygon.on('dragend', function() {
    saveFeatureGeometry(type, area, this)
  })
  
  shapesLayer.add(polygon)
}

// 绘制单个设施
const drawFacility = (facility) => {
  if (!shapesLayer) return
  
  // 获取位置信息（兼容location和geometry两种格式）
  let x = 0
  let y = 0
  
  if (facility.location) {
    // 直接有location字段
    x = facility.location.x
    y = facility.location.y
  } else if (facility.geometry && facility.geometry.type === 'Point') {
    // 从geometry字段获取（GeoJSON Point格式）
    x = facility.geometry.coordinates[0]
    y = facility.geometry.coordinates[1]
  } else {
    return // 没有位置信息，不绘制
  }
  
  // 设置颜色
  const color = typeColors['facility']
  
  // 创建圆形表示设施
  const circle = new Konva.Circle({
    x: x,
    y: y,
    radius: 10,
    fill: `${color}80`,
    stroke: color,
    strokeWidth: 2,
    draggable: true,
    id: `facility-${facility.id}`
  })
  
  // 选中状态
  if (selectedFeature.value?.id === facility.id && selectedType.value === 'facility') {
    circle.strokeWidth(3)
    circle.shadowBlur(8)
    circle.shadowColor(color)
  }
  
  // 绑定事件
  circle.on('click', () => selectFeature('facility', facility))
  circle.on('dragend', function() {
    saveFacilityLocation(facility, this)
  })
  
  shapesLayer.add(circle)
}

// 保存要素几何数据
const saveFeatureGeometry = async (type, area, shape) => {
  if (!shape || !area) return
  
  const points = shape.points()
  const coords = []
  
  for (let i = 0; i < points.length; i += 2) {
    coords.push([points[i], points[i + 1]])
  }
  
  // 添加闭合点
  if (coords.length > 0 && JSON.stringify(coords[0]) !== JSON.stringify(coords[coords.length - 1])) {
    coords.push([...coords[0]])
  }
  
  // 更新本地数据
  area.geometry = {
    type: 'Polygon',
    coordinates: [coords]
  }
  
  // 保存到后端
  try {
    // 根据类型选择对应的更新方法
    const updateFunctions = {
      storearea: managementAPI.updateManagementStorearea,
      eventarea: managementAPI.updateManagementEventarea,
      otherarea: managementAPI.updateManagementOtherarea
    }
    
    const updateFunction = updateFunctions[type]
    if (updateFunction) {
      await updateFunction(area.id, area)
    }
  } catch (error) {
    console.error('保存区域几何数据失败:', error)
    errorMessage.value = `保存区域几何数据失败: ${error.message || '未知错误'}`
  }
}

// 保存设施位置
const saveFacilityLocation = async (facility, shape) => {
  if (!shape || !facility) return
  
  // 更新本地数据
  facility.location = {
    x: shape.x(),
    y: shape.y()
  }
  
  // 保存到后端
  try {
    await managementAPI.updateManagementFacility(facility.id, facility)
  } catch (error) {
    console.error('保存设施位置失败:', error)
    errorMessage.value = `保存设施位置失败: ${error.message || '未知错误'}`
  }
}

// 合并区域数据（地图数据和管理API数据）
const mergeAreaData = (mapData, managementData, mapId) => {
  // 如果地图数据包含区域信息，则优先使用地图数据
  if (mapData && mapData.length > 0) {
    // 如果管理API有更多数据，也合并进来
    if (managementData && managementData.length > 0) {
      const mapDataById = new Map(mapData.map(item => [item.id, item]))
      
      managementData.forEach(item => {
        if (!mapDataById.has(item.id)) {
          // 如果管理API中的项目不在地图数据中，添加到地图数据
          mapDataById.set(item.id, item)
        } else {
          // 如果存在，合并管理API中的非几何属性
          const existingItem = mapDataById.get(item.id)
          Object.assign(existingItem, item)
        }
      })
      
      return Array.from(mapDataById.values())
    }
    return mapData
  }
  
  // 如果地图数据没有区域信息，使用管理API数据
  return managementData || []
}

// 合并设施数据（地图数据和管理API数据）
const mergeFacilityData = (mapData, managementData, mapId) => {
  // 如果地图数据包含设施信息，则优先使用地图数据
  if (mapData && mapData.length > 0) {
    // 如果管理API有更多数据，也合并进来
    if (managementData && managementData.length > 0) {
      const mapDataById = new Map(mapData.map(item => [item.id, item]))
      
      managementData.forEach(item => {
        if (!mapDataById.has(item.id)) {
          // 如果管理API中的项目不在地图数据中，添加到地图数据
          mapDataById.set(item.id, item)
        } else {
          // 如果存在，合并管理API中的非几何属性
          const existingItem = mapDataById.get(item.id)
          Object.assign(existingItem, item)
        }
      })
      
      return Array.from(mapDataById.values())
    }
    return mapData
  }
  
  // 如果地图数据没有设施信息，使用管理API数据
  return managementData || []
}

// 添加舞台事件
const addStageEvents = (Konva) => {
  if (!stage) return
  
  // 缩放功能
  let scaleBy = 1.1
  
  stage.on('wheel', (e) => {
    e.evt.preventDefault()
    
    const oldScale = stage.scaleX()
    const pointer = stage.getPointerPosition()
    
    const mousePointTo = {
      x: (pointer.x - stage.x()) / oldScale,
      y: (pointer.y - stage.y()) / oldScale
    }
    
    const direction = e.evt.deltaY > 0 ? 1 : -1
    const newScale = direction > 0 ? oldScale / scaleBy : oldScale * scaleBy
    
    stage.scale({ x: newScale, y: newScale })
    
    const newPos = {
      x: pointer.x - mousePointTo.x * newScale,
      y: pointer.y - mousePointTo.y * newScale
    }
    
    stage.position(newPos)
    stage.batchDraw()
  })
}

// 保存属性
const saveAttributes = async () => {
  if (!selectedFeature.value || !selectedType.value) return
  
  submitting.value = true
  errorMessage.value = ''
  
  try {
    // 准备提交数据
    const submitData = {
      name: form.name,
      description: form.description,
      is_active: form.is_active
    }
    
    // 根据类型设置特定字段
    if (selectedType.value === 'storearea') {
      submitData.store_name = form.name
      submitData.store_type = parseInt(form.type)
      delete submitData.name
    } else if (selectedType.value === 'eventarea') {
      submitData.event_name = form.name
      submitData.event_type = parseInt(form.type)
      delete submitData.name
    } else if (selectedType.value === 'otherarea') {
      submitData.type_id = parseInt(form.type)
    } else if (selectedType.value === 'facility') {
      submitData.description = form.name
      submitData.type = parseInt(form.type)
      delete submitData.name
    }
    
    // 更新后端数据
    await managementAPI.updateAreaByTypeAndId(selectedType.value, selectedFeature.value.id, submitData)
    
    // 更新本地数据
    if (selectedType.value === 'storearea') {
      selectedFeature.value.store_name = form.name
      selectedFeature.value.store_type = parseInt(form.type)
    } else if (selectedType.value === 'eventarea') {
      selectedFeature.value.event_name = form.name
      selectedFeature.value.event_type = parseInt(form.type)
    } else if (selectedType.value === 'otherarea') {
      selectedFeature.value.name = form.name
      selectedFeature.value.type_id = parseInt(form.type)
    } else if (selectedType.value === 'facility') {
      selectedFeature.value.description = form.name
      selectedFeature.value.type = parseInt(form.type)
    }
    
    selectedFeature.value.description = form.description
    selectedFeature.value.is_active = form.is_active
    
    // 重新绘制
    drawAreas()
  } catch (error) {
    console.error('保存属性失败:', error)
    errorMessage.value = `保存属性失败: ${error.response?.data?.error || error.message || '未知错误'}`
  } finally {
    submitting.value = false
  }
}

// 关闭创建模态框
const closeCreateModal = () => {
  showCreateModal.value = false
  errorMessage.value = ''
  
  // 重置表单
  createForm.type = 'storearea'
  createForm.shape = 'square'
  createForm.size = 20
}

// 处理创建区域
const handleCreateArea = async () => {
  if (!currentMapId.value) {
    errorMessage.value = '请先选择地图'
    return
  }
  
  submitting.value = true
  errorMessage.value = ''
  
  try {
    // 生成几何数据
    const geometry = generateGeometry(createForm.shape, createForm.size)
    
    // 准备创建数据
    const createData = {
      map_id: currentMapId.value,
      geometry: geometry,
      description: '',
      is_active: true
    }
    
    // 根据类型设置特定字段
    if (createForm.type === 'storearea') {
      createData.store_name = '新店铺'
      createData.store_type = 0
    } else if (createForm.type === 'eventarea') {
      createData.event_name = '新活动区域'
      createData.event_type = 0
    } else if (createForm.type === 'otherarea') {
      createData.name = '新区域'
      createData.type_id = 0
    }
    
    // 这里可以添加创建到后端的逻辑
    // const response = await createArea(createForm.type, createData)
    
    // 模拟创建成功
    const newArea = {
      id: Date.now(),
      ...createData
    }
    
    // 添加到本地数据
    if (createForm.type === 'storearea') {
      storeareas.value.push(newArea)
    } else if (createForm.type === 'eventarea') {
      eventareas.value.push(newArea)
    } else if (createForm.type === 'otherarea') {
      otherareas.value.push(newArea)
    }
    
    // 重新绘制
    drawAreas()
    
    // 关闭模态框
    closeCreateModal()
  } catch (error) {
    console.error('创建区域失败:', error)
    errorMessage.value = `创建区域失败: ${error.response?.data?.error || error.message || '未知错误'}`
  } finally {
    submitting.value = false
  }
}

// 生成几何数据
const generateGeometry = (shape, size) => {
  const centerX = stage ? stage.width() / 2 : 200
  const centerY = stage ? stage.height() / 2 : 200
  const coords = []
  
  switch (shape) {
    case 'square':
      coords.push([centerX - size, centerY - size])
      coords.push([centerX + size, centerY - size])
      coords.push([centerX + size, centerY + size])
      coords.push([centerX - size, centerY + size])
      break
    
    case 'rect':
      coords.push([centerX - size * 1.5, centerY - size])
      coords.push([centerX + size * 1.5, centerY - size])
      coords.push([centerX + size * 1.5, centerY + size])
      coords.push([centerX - size * 1.5, centerY + size])
      break
    
    case 'circle':
      // 简化为正多边形
      const sides = 12
      for (let i = 0; i < sides; i++) {
        const angle = (i / sides) * Math.PI * 2
        coords.push([
          centerX + Math.cos(angle) * size,
          centerY + Math.sin(angle) * size
        ])
      }
      break
    
    case 'triangle':
      coords.push([centerX, centerY - size])
      coords.push([centerX + size, centerY + size])
      coords.push([centerX - size, centerY + size])
      break
    
    case 'hexagon':
      const hexSides = 6
      for (let i = 0; i < hexSides; i++) {
        const angle = (i / hexSides) * Math.PI * 2
        coords.push([
          centerX + Math.cos(angle) * size,
          centerY + Math.sin(angle) * size
        ])
      }
      break
  }
  
  // 添加闭合点
  if (coords.length > 0) {
    coords.push([...coords[0]])
  }
  
  return {
    type: 'Polygon',
    coordinates: [coords]
  }
}

// 初始化
onMounted(() => {
  loadMaps()
})
</script>

<style scoped>
.map-editor {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8fafc;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #ffffff;
  border-bottom: 1px solid #e2e8f0;
}

.title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
}

.actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.map-selector {
  display: flex;
  align-items: center;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background-color: #ffffff;
}

.map-editor-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 280px;
  background-color: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.sidebar-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: #374151;
}

.layer-groups {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.layer-group {
  margin-bottom: 0.5rem;
  border-radius: 0.375rem;
  overflow: hidden;
}

.layer-group-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #f3f4f6;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.layer-icon {
  font-size: 1rem;
}

.layer-count {
  margin-left: auto;
  font-size: 0.75rem;
  color: #6b7280;
}

.layer-toggle {
  font-size: 0.75rem;
  color: #6b7280;
  transition: transform 0.2s;
}

.layer-items {
  padding: 0.25rem 0;
  background-color: #f9fafb;
}

.layer-item {
  padding: 0.5rem 1.5rem;
  font-size: 0.875rem;
  color: #4b5563;
  cursor: pointer;
  transition: background-color 0.2s;
}

.layer-item:hover {
  background-color: #f3f4f6;
}

.layer-item.selected {
  background-color: #dbeafe;
  color: #1e40af;
  border-right: 3px solid #3b82f6;
}

.map-canvas-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  background-color: #f1f5f9;
}

.map-canvas-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.konva-stage-container {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}

.properties-panel {
  width: 320px;
  background-color: #ffffff;
  border-left: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.panel-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: #374151;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.properties-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.form-input,
.form-select,
.form-textarea {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background-color: #ffffff;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.toggle-switch {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toggle-input {
  position: absolute;
  opacity: 0;
}

.toggle-label {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
  background-color: #d1d5db;
  border-radius: 12px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.toggle-label::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background-color: #ffffff;
  border-radius: 50%;
  transition: transform 0.3s;
}

.toggle-input:checked + .toggle-label {
  background-color: #3b82f6;
}

.toggle-input:checked + .toggle-label::after {
  transform: translateX(24px);
}

.toggle-text {
  font-size: 0.875rem;
  color: #6b7280;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: #ffffff;
  border-radius: 0.5rem;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  transition: background-color 0.2s;
}

.modal-close:hover {
  background-color: #f3f4f6;
}

.modal-body {
  padding: 1.5rem;
}

.shape-templates {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.shape-template {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.shape-template:hover {
  border-color: #93c5fd;
  background-color: #eff6ff;
}

.shape-template.selected {
  border-color: #3b82f6;
  background-color: #dbeafe;
}

.template-icon {
  font-size: 2rem;
}

.template-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #374151;
}

.size-control {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.size-slider {
  flex: 1;
}

.size-value {
  font-size: 0.875rem;
  color: #6b7280;
  min-width: 30px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #3b82f6;
  color: #ffffff;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: #6b7280;
  color: #ffffff;
}

.btn-secondary:hover {
  background-color: #4b5563;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 1rem;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  padding: 0.75rem;
  background-color: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 0.375rem;
  color: #dc2626;
  font-size: 0.875rem;
}

.loading-container,
.panel-empty,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 1rem;
  color: #6b7280;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(59, 130, 246, 0.3);
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.empty-icon {
  font-size: 3rem;
  opacity: 0.5;
}
</style>