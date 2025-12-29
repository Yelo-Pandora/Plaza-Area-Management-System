import { reactive } from 'vue'
import { useMapEditorStore } from '../../composables/useMapEditorStore'

export function useSidebarLogic() {
  const {
    storeareas, eventareas, otherareas, facilities,
    selectFeature, selectedFeature, selectedType
  } = useMapEditorStore()

  const expandedLayers = reactive({
    storearea: true,
    eventarea: true,
    otherarea: true,
    facility: true
  })

  const toggleLayer = (type) => {
    expandedLayers[type] = !expandedLayers[type]
  }

  const handleSelect = (type, item) => {
    selectFeature(type, item)
  }

  const isSelected = (type, id) => {
    return selectedType.value === type && selectedFeature.value?.id === id
  }

  // 字符串截断函数：超过 len 个字就加省略号
  const truncate = (str, len = 6) => {
    if (!str) return ''
    return str.length > len ? str.substring(0, len) + '...' : str
  }

  // 获取活动区域显示文本：类型 (描述)
  const getEventAreaDisplay = (area) => {
    const typeMap = {
      0: '普通活动',
      1: '促销活动',
      2: '展览活动',
      3: '表演活动'
    }
    // 兼容字符串或数字类型的 type
    const typeName = typeMap[area.type] || '活动区域'
    const desc = area.description ? ` (${truncate(area.description)})` : ''
    return typeName + desc
  }

  // 获取其他区域显示文本：类型 (描述)
  const getOtherAreaDisplay = (area) => {
    const typeMap = {
      0: '公共区域',
      1: '办公区域',
      2: '设备区域',
      3: '其他区域'
    }
    const typeName = typeMap[area.type] || '其他区域'
    const desc = area.description ? ` (${truncate(area.description)})` : ''
    return typeName + desc
  }

  return {
    storeareas,
    eventareas,
    otherareas,
    facilities,
    expandedLayers,
    toggleLayer,
    handleSelect,
    isSelected,
    // 导出新函数供模板使用
    getEventAreaDisplay,
    getOtherAreaDisplay
  }
}
