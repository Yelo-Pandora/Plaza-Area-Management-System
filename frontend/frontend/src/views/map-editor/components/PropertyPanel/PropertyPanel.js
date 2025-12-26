import { reactive, ref, watch } from 'vue'
import { useMapEditorStore } from '../../composables/useMapEditorStore'
import * as managementAPI from '@/api/management'
import * as editorAPI from '@/api/editor' // 引入 editorAPI 用于删除

export function usePropertiesLogic() {
  const {
    selectedFeature,
    selectedType,
    updateLocalFeature,
    // 引入 store 中的数据引用，用于本地删除
    storeareas, eventareas, otherareas, facilities,
    selectFeature,
    loadCurrentMap // 用于删除后刷新
  } = useMapEditorStore()

  const submitting = ref(false)
  const isDeleting = ref(false) // 新增删除状态
  const errorMessage = ref('')

  const form = reactive({
    name: '',
    type: '0',
    description: '',
    is_active: true
  })

  const typeNames = {
    storearea: '店铺',
    eventarea: '活动区域',
    otherarea: '其他区域',
    facility: '设施'
  }

  const getTypeName = () => typeNames[selectedType.value] || '区域'

  // 监听选中变更
  watch(selectedFeature, (newVal) => {
    if (newVal) {
      form.name = newVal.name || newVal.store_name || newVal.event_name || newVal.description || ''
      form.type = newVal.store_type?.toString() || newVal.type_id?.toString() || newVal.event_type?.toString() || newVal.type?.toString() || '0'
      form.description = newVal.description || ''
      form.is_active = newVal.is_active !== undefined ? newVal.is_active : true
    }
  })

  // --- 新增：判断是否为新建元素 ---
  const isNewItem = (id) => {
    return String(id).length > 10 // 简单判断：时间戳ID通常很长
  }

  // --- 新增：删除逻辑 ---
  const handleDelete = async () => {
    if (!selectedFeature.value || !confirm(`确定要删除这个${getTypeName()}吗？此操作不可恢复。`)) return

    isDeleting.value = true
    errorMessage.value = ''
    const id = selectedFeature.value.id
    const type = selectedType.value

    try {
      if (isNewItem(id)) {
        // A. 如果是新建但未保存的元素 -> 直接从前端数组移除
        const targetListMap = {
          'storearea': storeareas,
          'eventarea': eventareas,
          'otherarea': otherareas,
          'facility': facilities
        }
        const listRef = targetListMap[type]
        if (listRef) {
          const index = listRef.value.findIndex(item => item.id === id)
          if (index !== -1) listRef.value.splice(index, 1)
        }
      } else {
        // B. 如果是已保存的元素 -> 调用后端 API
        if (type === 'storearea') await editorAPI.deleteEditorStorearea(id)
        else if (type === 'eventarea') await editorAPI.deleteEditorEventarea(id)
        else if (type === 'otherarea') await editorAPI.deleteEditorOtherarea(id)
        else if (type === 'facility') await editorAPI.deleteEditorFacility(id)

        // 删除成功后刷新地图
        await loadCurrentMap()
      }

      // 清空选中状态
      selectFeature('', null)

    } catch (error) {
      console.error('删除失败:', error)
      errorMessage.value = `删除失败: ${error.message || '未知错误'}`
    } finally {
      isDeleting.value = false
    }
  }

  const save = async () => {
    // ... (保留原有的 save 逻辑不变) ...
    // ... 略 ...
    // 原有代码:
    if (!selectedFeature.value || !selectedType.value) return
    submitting.value = true
    errorMessage.value = ''

    try {
      const submitData = {
        name: form.name,
        description: form.description,
        is_active: form.is_active
      }

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

      // 如果是新元素，提示先保存画布
      if (isNewItem(selectedFeature.value.id)) {
        alert('这是新建元素，请先点击地图上方的“保存更改”按钮将其持久化到数据库，然后再修改属性。')
        return
      }

      await managementAPI.updateAreaByTypeAndId(selectedType.value, selectedFeature.value.id, submitData)

      const localUpdate = { ...submitData }
      if (selectedType.value === 'storearea') localUpdate.store_name = form.name
      else if (selectedType.value === 'eventarea') localUpdate.event_name = form.name
      else if (selectedType.value === 'otherarea') localUpdate.name = form.name

      updateLocalFeature(localUpdate)
      alert('属性更新成功')

    } catch (error) {
      console.error('保存属性失败:', error)
      errorMessage.value = `保存失败: ${error.message || '未知错误'}`
    } finally {
      submitting.value = false
    }
  }

  return {
    form,
    selectedFeature,
    selectedType,
    save,
    handleDelete, // 导出
    submitting,
    isDeleting,   // 导出
    errorMessage,
    getTypeName
  }
}
