import { useMapEditorStore } from '../../composables/useMapEditorStore'

export function useHeaderLogic() {
  const { maps, currentMapId, loadCurrentMap } = useMapEditorStore()

  const handleChange = async () => {
    if (!currentMapId.value) return
    await loadCurrentMap()
  }

  return {
    maps,
    currentMapId,
    handleChange
  }
}
