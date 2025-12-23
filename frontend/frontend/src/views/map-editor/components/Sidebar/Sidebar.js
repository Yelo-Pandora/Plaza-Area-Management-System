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

  return {
    storeareas,
    eventareas,
    otherareas,
    facilities,
    expandedLayers,
    toggleLayer,
    handleSelect,
    isSelected
  }
}
