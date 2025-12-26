import { ref } from 'vue'
import { useMapEditorStore } from '../../composables/useMapEditorStore'
import * as editorAPI from '@/api/editor'
import { validateBatchGeometry } from '@/api/map'

export function useMapSaveLogic() {
  const {
    currentMapId,
    storeareas,
    eventareas,
    otherareas,
    facilities,
    loadCurrentMap // 引入重新加载函数
  } = useMapEditorStore()

  const isSaving = ref(false)

  const backendTypeMap = {
    'storearea': 'store',
    'eventarea': 'event',
    'otherarea': 'other',
    'facility': 'facility'
  }

  const getName = (item) => {
    return item.name || item.store_name || item.event_name || item.description || '未命名'
  }

  // --- 转换几何为 WKT ---
  const toWKT = (item) => {
    // 1. 设施 (Point)
    if (item._type === 'facility') {
      const loc = item.location
      let x, y
      if (loc && typeof loc.x === 'number') { x = loc.x; y = loc.y }
      else if (loc && loc.type === 'Point') { [x, y] = loc.coordinates }
      else if (item.geometry && item.geometry.type === 'Point') { [x, y] = item.geometry.coordinates }

      if (x !== undefined && y !== undefined) return `POINT (${x} ${y})`
      return null
    }
    // 2. 区域 (Polygon)
    const geo = item.geometry
    if (!geo) return null
    let rings = []
    if (geo.type === 'Polygon') rings = geo.coordinates
    else if (geo.type === 'MultiPolygon') rings = geo.coordinates[0]

    if (rings && rings.length > 0) {
      const coordsStr = rings[0].map(p => `${p[0]} ${p[1]}`).join(', ')
      return `POLYGON ((${coordsStr}))`
    }
    return null
  }

  // --- 判断是否为新元素 ---
  // 依据：ID 是时间戳 (13位) 肯定比数据库自增 ID (通常 < 10位) 大
  const isNewItem = (id) => {
    return String(id).length > 10
  }

  // --- 智能保存单个元素 (Create 或 Update) ---
  const saveItem = async (item, type) => {
    const wktData = toWKT(item)
    const mapId = currentMapId.value

    // 判断是新建还是更新
    if (isNewItem(item.id)) {
      // === 新建逻辑 ===
      console.log(`正在创建新元素: ${type}`)
      if (type === 'storearea') {
        return editorAPI.createEditorStorearea(wktData, mapId)
      } else if (type === 'eventarea') {
        return editorAPI.createEditorEventarea(wktData, mapId)
      } else if (type === 'otherarea') {
        // 传入 item.type (其他区域类型)
        return editorAPI.createEditorOtherarea(wktData, mapId, item.type || 0)
      } else if (type === 'facility') {
        // 传入 item.type (设施类型)
        return editorAPI.createEditorFacility(wktData, mapId, item.type || 0)
      }
    } else {
      // === 更新逻辑 ===
      if (type === 'storearea') {
        return editorAPI.updateEditorStoreareaShape(item.id, wktData)
      } else if (type === 'eventarea') {
        return editorAPI.updateEditorEventareaShape(item.id, wktData)
      } else if (type === 'otherarea') {
        return editorAPI.updateEditorOtherareaShape(item.id, wktData)
      } else if (type === 'facility') {
        return editorAPI.updateEditorFacilityLocation(item.id, wktData)
      }
    }
  }

  // --- 主保存函数 ---
  const handleSaveAll = async () => {
    if (!currentMapId.value) {
      alert('未选择地图')
      return
    }

    isSaving.value = true

    try {
      // 1. 收集所有数据
      const allItems = [
        ...storeareas.value.map(i => ({ ...i, _type: 'storearea' })),
        ...eventareas.value.map(i => ({ ...i, _type: 'eventarea' })),
        ...otherareas.value.map(i => ({ ...i, _type: 'otherarea' })),
        ...facilities.value.map(i => ({ ...i, _type: 'facility' }))
      ]

      // 2. 构造批量校验请求
      const updates = []
      let hasNewItems = false

      for (const item of allItems) {
        const wkt = toWKT(item)
        if (wkt) {
          // 如果是新元素，校验时给个假ID (避免 ID='1703...' 导致后端转换int报错或逻辑混乱)
          // 或者直接传临时ID，只要后端 validate_batch 的 updated_keys 逻辑能处理字符串即可(我们在上一步已经修复了后端支持str id)
          // 为了保险，新元素我们不做“排除旧位置”的校验（因为它没有旧位置），这在后端 validate_batch 逻辑天然支持

          if (isNewItem(item.id)) hasNewItems = true;

          updates.push({
            id: item.id,
            type: backendTypeMap[item._type] || item._type,
            name: getName(item),
            geometry: wkt
          })
        }
      }

      if (updates.length === 0) {
        alert('没有可保存的数据')
        isSaving.value = false
        return
      }

      // 3. 发送校验
      console.log('正在发送批量校验请求...', updates)
      const validateRes = await validateBatchGeometry({
        map_id: currentMapId.value,
        updates: updates
      })

      if (validateRes && validateRes.valid === false) {
        const errors = validateRes.errors || []
        const errorMsg = `保存被拒绝，发现 ${errors.length} 个问题：\n\n` +
          errors.slice(0, 5).join('\n') +
          (errors.length > 5 ? `\n...等共 ${errors.length} 个问题` : '')
        alert(errorMsg)
        isSaving.value = false
        return
      }

      // 4. 执行保存 (Create 或 Update)
      const savePromises = allItems
        .filter(item => toWKT(item))
        .map(item => saveItem(item, item._type))

      await Promise.all(savePromises)

      // 5. 关键：如果包含新创建的元素，必须重新加载地图
      // 否则新元素在前端还是临时ID，下次保存会重复创建
      if (hasNewItems) {
        console.log('检测到新建元素，正在刷新地图数据以同步ID...')
        await loadCurrentMap()
      }

      alert('保存成功！')

    } catch (error) {
      console.error('保存过程出错:', error)
      let msg = error.message
      if (error.data && error.data.error) {
        msg = error.data.error
      }
      alert(`保存出错: ${msg}`)
    } finally {
      isSaving.value = false
    }
  }

  return {
    handleSaveAll,
    isSaving
  }
}
