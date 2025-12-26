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
    facilities
  } = useMapEditorStore()

  const isSaving = ref(false)

  // 类型映射
  const backendTypeMap = {
    'storearea': 'store',
    'eventarea': 'event',
    'otherarea': 'other',
    'facility': 'facility'
  }

  const getName = (item) => {
    return item.name || item.store_name || item.event_name || item.description || '未命名'
  }

  // --- 核心修改：将几何数据转换为 WKT (Well-Known Text) 格式 ---
  // WKT 格式不带 SRID 信息，后端 GEOSGeometry(wkt, srid=2385) 可以直接接受
  const toWKT = (item) => {
    // 1. 处理设施 (Point)
    if (item._type === 'facility') {
      const loc = item.location
      let x, y

      // 处理 {x, y} 对象 (Konva 拖拽后的格式)
      if (loc && typeof loc.x === 'number') {
        x = loc.x
        y = loc.y
      }
      // 处理 GeoJSON Point (初始加载的格式)
      else if (loc && loc.type === 'Point') {
        [x, y] = loc.coordinates
      }
      // 处理 GeoJSON Point 在 geometry 字段的情况
      else if (item.geometry && item.geometry.type === 'Point') {
        [x, y] = item.geometry.coordinates
      }

      if (x !== undefined && y !== undefined) {
        return `POINT (${x} ${y})`
      }
      return null
    }

    // 2. 处理区域 (Polygon)
    const geo = item.geometry
    if (!geo) return null

    let rings = []

    // 提取坐标数组
    if (geo.type === 'Polygon') {
      rings = geo.coordinates
    } else if (geo.type === 'MultiPolygon') {
      // 简化处理：只取第一个多边形的外环
      // 这里的逻辑假设商铺等都是单多边形
      rings = geo.coordinates[0]
    }

    if (rings && rings.length > 0) {
      // rings[0] 是外环
      // 格式转换: [[x1, y1], [x2, y2]] -> "x1 y1, x2 y2"
      const coordsStr = rings[0].map(p => `${p[0]} ${p[1]}`).join(', ')
      return `POLYGON ((${coordsStr}))`
    }

    return null
  }

  // 单个保存 API 调用
  const saveItem = async (item, type) => {
    // 获取 WKT 字符串
    const wktData = toWKT(item)

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

      // 2. 构造批量校验请求数据 (全部转为 WKT)
      const updates = []

      for (const item of allItems) {
        const wkt = toWKT(item)
        if (wkt) {
          updates.push({
            id: item.id,
            type: backendTypeMap[item._type] || item._type,
            name: getName(item),
            geometry: wkt // 发送 WKT 字符串
          })
        }
      }

      if (updates.length === 0) {
        alert('没有可保存的数据')
        isSaving.value = false
        return
      }

      console.log('正在发送批量校验请求(WKT)...', updates)

      // 3. 发送后端批量校验
      // 后端 map/services.py 中的 GEOSGeometry(geo_str) 也能完美兼容 WKT
      const validateRes = await validateBatchGeometry({
        map_id: currentMapId.value,
        updates: updates
      })

      // 4. 处理校验结果
      if (validateRes && validateRes.valid === false) {
        const errors = validateRes.errors || []
        const errorMsg = `保存被拒绝，发现 ${errors.length} 个问题：\n\n` +
                         errors.slice(0, 10).join('\n') +
                         (errors.length > 10 ? `\n...等共 ${errors.length} 个问题` : '')
        alert(errorMsg)
        isSaving.value = false
        return
      }

      // 5. 校验通过，执行并发保存
      const savePromises = allItems
        .filter(item => toWKT(item)) // 再次过滤确保有几何数据
        .map(item => saveItem(item, item._type))

      await Promise.all(savePromises)

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
