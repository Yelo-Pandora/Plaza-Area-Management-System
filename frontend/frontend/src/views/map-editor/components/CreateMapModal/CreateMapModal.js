import { reactive, ref } from 'vue'
import { createMapInEditor } from '@/api/editor'
import { useMapEditorStore } from '../../composables/useMapEditorStore'

export function useCreateMapLogic(props, emit) {
  const { loadMaps, currentMapId } = useMapEditorStore()

  const submitting = ref(false)
  const error = ref('')
  const file = ref(null)

  const form = reactive({
    building_id: '',
    floor_number: '',
    mode: 'manual' // 'manual' | 'import'
  })

  // 重置表单
  const resetForm = () => {
    form.building_id = ''
    form.floor_number = ''
    form.mode = 'manual'
    file.value = null
    error.value = ''
    // 重置文件输入框的值，防止重复选择同一文件不触发change
    const fileInput = document.querySelector('.file-input')
    if (fileInput) fileInput.value = ''
  }

  const close = () => {
    emit('update:visible', false)
    resetForm()
  }

  const handleFileChange = (e) => {
    const selected = e.target.files[0]
    if (selected) {
      if (!selected.name.toLowerCase().endsWith('.dxf')) {
        alert('请上传 .dxf 格式的 CAD 文件')
        e.target.value = ''
        file.value = null
      } else {
        file.value = selected
      }
    }
  }

  // 辅助函数：读取文件为 Base64 字符串
  const readFileAsBase64 = (fileObj) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result)
      reader.onerror = (err) => reject(err)
      reader.readAsDataURL(fileObj)
    })
  }

  const handleSubmit = async () => {
    submitting.value = true
    error.value = ''

    try {
      // 1. 构建 payload (使用 JSON 传输)
      const payload = {
        building_id: form.building_id,
        floor_number: form.floor_number,
        file_data: null
      }

      // 2. 如果是导入模式，将文件转为 Base64
      if (form.mode === 'import') {
        if (!file.value) {
          throw new Error('请选择 DXF 文件')
        }
        payload.file_data = await readFileAsBase64(file.value)
      }

      // 3. 发送请求
      const res = await createMapInEditor(payload)

      alert('地图创建成功')

      // 4. 刷新数据并切换
      await loadMaps()
      if (res && res.id) {
        currentMapId.value = res.id
      }

      close()

    } catch (err) {
      console.error(err)
      const apiMsg = err.data?.error || err.message
      error.value = apiMsg || '创建失败，请检查输入'
    } finally {
      submitting.value = false
    }
  }

  return {
    form,
    submitting,
    error,
    close,
    handleFileChange,
    handleSubmit
  }
}
