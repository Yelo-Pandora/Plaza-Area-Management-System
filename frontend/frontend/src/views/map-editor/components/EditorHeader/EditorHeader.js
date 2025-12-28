import { useMapEditorStore } from '../../composables/useMapEditorStore'
import { deleteMapInEditor } from '@/api/editor'
import { ref } from 'vue'

export function useHeaderLogic() {
  const { maps, currentMapId, loadCurrentMap, resetMapState } = useMapEditorStore()

  const showCreateMap = ref(false)

  const handleChange = async () => {
    if (!currentMapId.value) return
    await loadCurrentMap()
  }

  // 处理删除点击
  const handleDeleteMap = async () => {
    const mapId = currentMapId.value
    if (!mapId) return

    const confirmed = window.confirm('确定要删除当前地图吗？\n警告：该地图上的所有店铺、设施和区域也将被一并删除！')
    if (!confirmed) return

    try {
      // 调用 API
      await deleteMapInEditor(mapId)
      // 调用Store方法清理状态
      resetMapState(mapId)
    } catch (e) {
      console.error(e)
      alert('删除失败: ' + (e.message || '未知错误'))
    }
  }

  return {
    maps,
    currentMapId,
    handleChange,
    showCreateMap,
    handleDeleteMap,
  }
}
