import { useMapEditorStore } from '../../composables/useMapEditorStore'
import { ref } from 'vue'

export function useHeaderLogic() {
  const { maps, currentMapId, loadCurrentMap } = useMapEditorStore()

  const showCreateMap = ref(false)

  const handleChange = async () => {
    if (!currentMapId.value) return
    await loadCurrentMap()
  }

  return {
    maps,
    currentMapId,
    handleChange,
    showCreateMap
  }
}
