import { reactive, ref, watch } from 'vue'
import { useMapEditorStore } from '../../composables/useMapEditorStore'
import * as managementAPI from '@/api/management'

export function usePropertiesLogic() {
  const { selectedFeature, selectedType, updateLocalFeature } = useMapEditorStore()
  const submitting = ref(false)
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

  // 监听选中变更，回填表单
  watch(selectedFeature, (newVal) => {
    if (newVal) {
      form.name = newVal.name || newVal.store_name || newVal.event_name || newVal.description || ''
      form.type = newVal.store_type?.toString() || newVal.type_id?.toString() || newVal.event_type?.toString() || newVal.type?.toString() || '0'
      form.description = newVal.description || ''
      form.is_active = newVal.is_active !== undefined ? newVal.is_active : true
    }
  })

  const save = async () => {
    if (!selectedFeature.value || !selectedType.value) return
    submitting.value = true
    errorMessage.value = ''

    try {
      // 构造提交数据
      const submitData = {
        name: form.name,
        description: form.description,
        is_active: form.is_active
      }

      // 根据类型适配字段
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
        submitData.description = form.name // 设施通常用 description 作名称
        submitData.type = parseInt(form.type)
        delete submitData.name
      }

      // 调用 API
      await managementAPI.updateAreaByTypeAndId(selectedType.value, selectedFeature.value.id, submitData)

      // 更新本地数据，实现即时反馈
      const localUpdate = { ...submitData }
      // 还原回本地字段名
      if (selectedType.value === 'storearea') localUpdate.store_name = form.name
      else if (selectedType.value === 'eventarea') localUpdate.event_name = form.name
      else if (selectedType.value === 'otherarea') localUpdate.name = form.name

      updateLocalFeature(localUpdate)

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
    submitting,
    errorMessage,
    getTypeName
  }
}
