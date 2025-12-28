import { reactive, ref } from 'vue'
import { useMapEditorStore } from '../../composables/useMapEditorStore'

export function useCreateModalLogic(props, emit) {
  const { currentMapId, addLocalFeature } = useMapEditorStore()

  const submitting = ref(false)
  const errorMessage = ref('')

  const form = reactive({
    type: 'storearea',
    shape: 'square',
    size: 20
  })

  const shapeTemplates = [
    { label: '正方形', shape: 'square', icon: '◼️' },
    { label: '矩形', shape: 'rect', icon: '▭️' },
    { label: '圆形', shape: 'circle', icon: '⭕' },
    { label: '三角形', shape: 'triangle', icon: '🔺' },
    { label: '六边形', shape: 'hexagon', icon: '⬢' }
  ]

  const close = () => {
    emit('update:visible', false)
    errorMessage.value = ''
  }

  // 生成几何数据
  const generateGeometry = (shape, size) => {
    // 默认生成在画布中心，这里简化为固定坐标 (200, 200)
    // 实际项目中可从 store 获取 stage 宽高
    const centerX = 200
    const centerY = 200
    const coords = []

    switch (shape) {
      case 'square':
        coords.push([centerX - size, centerY - size])
        coords.push([centerX + size, centerY - size])
        coords.push([centerX + size, centerY + size])
        coords.push([centerX - size, centerY + size])
        break
      case 'rect':
        coords.push([centerX - size * 1.5, centerY - size])
        coords.push([centerX + size * 1.5, centerY - size])
        coords.push([centerX + size * 1.5, centerY + size])
        coords.push([centerX - size * 1.5, centerY + size])
        break
      case 'circle': // 近似多边形
        const sides = 12
        for (let i = 0; i < sides; i++) {
          const angle = (i / sides) * Math.PI * 2
          coords.push([
            centerX + Math.cos(angle) * size,
            centerY + Math.sin(angle) * size
          ])
        }
        break
      case 'triangle':
        coords.push([centerX, centerY - size])
        coords.push([centerX + size, centerY + size])
        coords.push([centerX - size, centerY + size])
        break
      case 'hexagon':
        for (let i = 0; i < 6; i++) {
          const angle = (i / 6) * Math.PI * 2
          coords.push([
            centerX + Math.cos(angle) * size,
            centerY + Math.sin(angle) * size
          ])
        }
        break
    }

    // 闭合
    if (coords.length > 0) {
      coords.push([...coords[0]])
    }

    return {
      type: 'Polygon',
      coordinates: [coords]
    }
  }

  const handleCreate = async () => {
    if (!currentMapId.value) {
      errorMessage.value = '请先选择地图'
      return
    }

    submitting.value = true
    try {
      const geometry = generateGeometry(form.shape, form.size)

      const createData = {
        map_id: currentMapId.value,
        geometry: geometry,
        description: '',
        is_active: true
      }

      // 设置默认名称
      if (form.type === 'storearea') {
        createData.store_name = '新店铺'
        createData.store_type = 0
      } else if (form.type === 'eventarea') {
        createData.event_name = '新活动区域'
        createData.event_type = 0
      } else if (form.type === 'otherarea') {
        createData.name = '新区域'
        createData.type_id = 0
      }

      // 模拟创建成功 (实际应调用 API)
      const newArea = {
        id: Date.now(),
        ...createData
      }

      addLocalFeature(form.type, newArea)
      close()

    } catch (error) {
      errorMessage.value = error.message
    } finally {
      submitting.value = false
    }
  }

  return { form, shapeTemplates, handleCreate, close, submitting, errorMessage }
}
