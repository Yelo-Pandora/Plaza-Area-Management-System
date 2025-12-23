import { ref, reactive } from 'vue'
import { listMaps, getMapById } from '@/api/map'
import * as managementAPI from '@/api/management'

// 定义全局响应式状态（单例模式，类似简易 Pinia）
const maps = ref([])
const currentMapId = ref('')
const currentMap = ref(null)
const loading = ref(false)

// 图层数据
const storeareas = ref([])
const eventareas = ref([])
const otherareas = ref([])
const facilities = ref([])

// 选中状态
const selectedType = ref('')
const selectedFeature = ref(null)

// 辅助函数：合并数据
const mergeData = (mapData, mgmtData) => {
  if (mapData && mapData.length > 0) {
    if (mgmtData && mgmtData.length > 0) {
      const mapDataById = new Map(mapData.map(item => [item.id, item]))
      mgmtData.forEach(item => {
        if (!mapDataById.has(item.id)) {
          mapDataById.set(item.id, item)
        } else {
          Object.assign(mapDataById.get(item.id), item)
        }
      })
      return Array.from(mapDataById.values())
    }
    return mapData
  }
  return mgmtData || []
}

export function useMapEditorStore() {

  // 加载地图列表
  const loadMaps = async () => {
    loading.value = true
    try {
      const response = await listMaps()
      maps.value = response.data || response
      if (maps.value.length > 0 && !currentMapId.value) {
        currentMapId.value = maps.value[0].id
        await loadCurrentMap()
      }
    } catch (error) {
      console.error('加载地图列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 加载当前地图详情及所有区域数据
  const loadCurrentMap = async () => {
    if (!currentMapId.value) return
    loading.value = true

    try {
      // 1. 获取地图详情 (包含 geometry)
      const mapRes = await getMapById(currentMapId.value)
      const mapData = mapRes.data || mapRes
      currentMap.value = mapData
      // 2. 获取管理数据 (包含属性)
      const [sData, eData, oData, fData] = await Promise.all([
        managementAPI.listManagementStoreareas(),
        managementAPI.listManagementEventareas(),
        managementAPI.listManagementOtherareas(),
        managementAPI.listManagementFacilities()
      ])

      const mapId = currentMapId.value

      // 3. 过滤并合并
      storeareas.value = mergeData(
        mapData.stores || mapData.storeareas,
        (sData.data || sData).filter(i => i.map_id == mapId)
      )
      eventareas.value = mergeData(
        mapData.events || mapData.eventareas,
        (eData.data || eData).filter(i => i.map_id == mapId)
      )
      otherareas.value = mergeData(
        mapData.other_areas || mapData.otherareas,
        (oData.data || oData).filter(i => i.map_id == mapId)
      )
      facilities.value = mergeData(
        mapData.facilities,
        (fData.data || fData).filter(i => i.map_id == mapId)
      )

      // 清空选中
      selectedFeature.value = null
      selectedType.value = ''
    } catch (error) {
      console.error('加载地图详情失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 选中功能
  const selectFeature = (type, feature) => {
    selectedType.value = type
    selectedFeature.value = feature
  }

  // 更新本地单个区域数据（用于保存属性后的即时回显）
  const updateLocalFeature = (updatedData) => {
    if (!selectedFeature.value) return
    Object.assign(selectedFeature.value, updatedData)
  }

  // 添加本地新区域
  const addLocalFeature = (type, feature) => {
    if (type === 'storearea') storeareas.value.push(feature)
    else if (type === 'eventarea') eventareas.value.push(feature)
    else if (type === 'otherarea') otherareas.value.push(feature)
  }

  return {
    maps,
    currentMapId,
    currentMap,
    loading,
    storeareas,
    eventareas,
    otherareas,
    facilities,
    selectedType,
    selectedFeature,
    loadMaps,
    loadCurrentMap,
    selectFeature,
    updateLocalFeature,
    addLocalFeature
  }
}
