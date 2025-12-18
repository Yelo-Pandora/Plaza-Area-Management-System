<!-- views/area-management/index.vue -->
<template>
  <div class="area-management">
    <div class="header">
      <h1 class="title">区域管理</h1>
      <div class="actions">
        <button class="btn btn-primary" @click="handleCreate">
          <span class="btn-icon">+</span> 新建区域
        </button>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-card">
      <div class="filter-row">
        <div class="filter-group">
          <label class="filter-label">区域类型</label>
          <select v-model="filters.type" class="filter-select" @change="handleFilterChange">
            <option value="">全部类型</option>
            <option value="storearea">店铺区域</option>
            <option value="eventarea">活动区域</option>
            <option value="otherarea">其他区域</option>
            <option value="event">活动</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label">地图楼层</label>
          <select v-model="filters.map_id" class="filter-select" @change="handleFilterChange">
            <option value="">全部楼层</option>
            <option v-for="map in mapList" :key="map.id" :value="map.id">
              楼层 {{ map.floor_number }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label">搜索名称</label>
          <div class="search-input-wrapper">
            <input
              v-model="filters.name"
              type="text"
              class="search-input"
              placeholder="输入区域名称..."
              @input="debounceSearch"
            >
            <span class="search-icon">🔍</span>
          </div>
        </div>
      </div>

      <div class="filter-row">
        <div class="filter-group">
          <label class="filter-label">状态筛选</label>
          <div class="status-buttons">
            <button
              :class="['status-btn', { active: filters.status === '' }]"
              @click="setStatus('')"
            >
              全部
            </button>
            <button
              :class="['status-btn', { active: filters.status === 'active' }]"
              @click="setStatus('active')"
            >
              启用
            </button>
            <button
              :class="['status-btn', { active: filters.status === 'inactive' }]"
              @click="setStatus('inactive')"
            >
              停用
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="table-container">
      <div class="table-header">
        <div class="table-row header-row">
          <div class="table-cell" style="flex: 0.5;">ID</div>
          <div class="table-cell" style="flex: 1.5;">名称</div>
          <div class="table-cell" style="flex: 1;">类型</div>
          <div class="table-cell" style="flex: 1;">地图楼层</div>
          <div class="table-cell" style="flex: 0.8;">状态</div>
          <div class="table-cell" style="flex: 1.5;">创建时间</div>
          <div class="table-cell" style="flex: 1.2;">操作</div>
        </div>
      </div>

      <div class="table-body">
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <span>加载中...</span>
        </div>

        <div v-else-if="areas.length === 0" class="empty-state">
          <span class="empty-icon">📋</span>
          <p>暂无区域数据</p>
        </div>

        <div v-else>
          <div
            v-for="area in paginatedAreas"
            :key="`${area.type}-${area.id}`"
            class="table-row data-row"
          >
            <div class="table-cell" style="flex: 0.5;">{{ area.id }}</div>
            <div class="table-cell" style="flex: 1.5;">
              <span class="area-name">{{ area.name || (area.store_name || area.event_name) || '未命名' }}</span>
            </div>
            <div class="table-cell" style="flex: 1;">
              <span :class="['type-badge', getTypeClass(area.type)]">
                {{ getTypeLabel(area) }}
              </span>
            </div>
            <div class="table-cell" style="flex: 1;">
              <span v-if="area.map_id" class="map-info">
                楼层 {{ getMapFloor(area.map_id) }}
              </span>
              <span v-else class="text-muted">未分配</span>
            </div>
            <div class="table-cell" style="flex: 0.8;">
              <span :class="['status-badge', area.is_active ? 'active' : 'inactive']">
                {{ area.is_active ? '启用' : '停用' }}
              </span>
            </div>
            <div class="table-cell" style="flex: 1.5;">
              {{ formatDate(area.created_at) }}
            </div>
            <div class="table-cell actions-cell" style="flex: 1.2;">
              <button class="action-btn edit-btn" @click="handleEdit(area)">
                编辑
              </button>
              <button class="action-btn view-btn" @click="handleViewOnMap(area)">
                查看
              </button>
              <button
                :class="['action-btn', area.is_active ? 'deactivate-btn' : 'activate-btn']"
                @click="toggleStatus(area)"
              >
                {{ area.is_active ? '停用' : '启用' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="areas.length > 0" class="pagination">
      <div class="pagination-info">
        显示 {{ (currentPage - 1) * pageSize + 1 }} -
        {{ Math.min(currentPage * pageSize, areas.length) }} 条，共 {{ areas.length }} 条
      </div>
      <div class="pagination-controls">
        <button
          :disabled="currentPage === 1"
          @click="currentPage--"
          class="pagination-btn"
        >
          上一页
        </button>
        <span class="pagination-current">{{ currentPage }} / {{ totalPages }}</span>
        <button
          :disabled="currentPage === totalPages"
          @click="currentPage++"
          class="pagination-btn"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 编辑/创建弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">{{ isEditing ? '编辑区域' : '创建区域' }}</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </div>

            <div class="form-group">
              <label class="form-label">区域类型</label>
              <select
                v-model="formData.type"
                class="form-select"
                :disabled="isEditing"
                required
                @change="onTypeChange"
              >
                <option value="storearea">店铺区域</option>
                <option value="eventarea">活动区域</option>
                <option value="otherarea">其他区域</option>
                <option value="event">活动</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">{{ getFormLabel('名称') }}</label>
              <input
                v-model="formData.name"
                type="text"
                class="form-input"
                :placeholder="`请输入${getFormLabel('名称')}`"
                required
              >
            </div>

            <div v-if="formData.type === 'storearea'" class="form-group">
              <label class="form-label">店铺类型</label>
              <select v-model="formData.store_type" class="form-select">
                <option value="0">普通店铺</option>
                <option value="1">餐饮</option>
                <option value="2">服饰</option>
                <option value="3">娱乐</option>
                <option value="4">服务</option>
              </select>
            </div>

            <div v-if="formData.type === 'otherarea'" class="form-group">
              <label class="form-label">其他区域类型</label>
              <select v-model="formData.type_id" class="form-select">
                <option value="0">公共区域</option>
                <option value="1">办公区域</option>
                <option value="2">设备区域</option>
                <option value="3">其他</option>
              </select>
            </div>

            <div v-if="formData.type === 'eventarea'" class="form-group">
              <label class="form-label">活动区域类型</label>
              <select v-model="formData.event_type" class="form-select">
                <option value="0">普通活动区域</option>
                <option value="1">促销活动</option>
                <option value="2">展览活动</option>
                <option value="3">表演活动</option>
              </select>
            </div>

            <div v-if="formData.type === 'event'" class="form-group">
              <label class="form-label">活动类型</label>
              <select v-model="formData.event_type" class="form-select">
                <option value="0">普通活动</option>
                <option value="1">促销活动</option>
                <option value="2">展览活动</option>
                <option value="3">表演活动</option>
              </select>
            </div>

            <div v-if="formData.type !== 'event'" class="form-group">
              <label class="form-label">所属地图</label>
              <select v-model="formData.map_id" class="form-select" required>
                <option value="">请选择地图楼层</option>
                <option v-for="map in mapList" :key="map.id" :value="map.id">
                  楼层 {{ map.floor_number }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">描述</label>
              <textarea
                v-model="formData.description"
                class="form-textarea"
                rows="3"
                :placeholder="`请输入${getFormLabel('描述')}`"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">状态</label>
              <div class="toggle-switch">
                <input
                  v-model="formData.is_active"
                  type="checkbox"
                  id="status-toggle"
                  class="toggle-input"
                >
                <label for="status-toggle" class="toggle-label">
                  <span class="toggle-slider"></span>
                  <span class="toggle-text">{{ formData.is_active ? '启用' : '停用' }}</span>
                </label>
              </div>
            </div>

            <div v-if="formData.type === 'storearea'" class="form-group">
              <label class="form-label">Logo URL</label>
              <input
                v-model="formData.logo_url"
                type="text"
                class="form-input"
                placeholder="请输入Logo URL"
              >
            </div>

            <div v-if="formData.type === 'event'" class="form-group">
              <label class="form-label">开始时间</label>
              <input
                v-model="formData.start_time"
                type="datetime-local"
                class="form-input"
                placeholder="请选择开始时间"
              >
            </div>

            <div v-if="formData.type === 'event'" class="form-group">
              <label class="form-label">结束时间</label>
              <input
                v-model="formData.end_time"
                type="datetime-local"
                class="form-input"
                placeholder="请选择结束时间"
              >
            </div>

            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="closeModal" :disabled="submitting">
                取消
              </button>
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting" class="btn-spinner"></span>
                {{ isEditing ? '保存更改' : '创建区域' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listMaps } from '../../api/map'
import * as managementAPI from '../../api/management'
import * as searchAPI from '../../api/search'

const router = useRouter()

// 数据状态
const areas = ref([])
const mapList = ref([])
const loading = ref(true)
const errorMessage = ref('')
const submitting = ref(false)

// 筛选条件
const filters = ref({
  type: '',
  map_id: '',
  name: '',
  status: ''
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 弹窗状态
const showModal = ref(false)
const isEditing = ref(false)
const formData = ref({
  id: null,
  type: 'storearea',
  name: '',
  map_id: '',
  store_type: '0',
  type_id: '0', // 用于otherarea
  event_type: '0', // 用于eventarea和event
  description: '',
  is_active: true,
  logo_url: '',
  start_time: '',
  end_time: ''
})

// 计算属性
const filteredAreas = computed(() => {
  return areas.value.filter(area => {
    // 按类型筛选
    if (filters.value.type && area.type !== filters.value.type) return false

    // 按地图筛选
    if (filters.value.map_id && area.map_id !== parseInt(filters.value.map_id)) return false

    // 按名称搜索
    if (filters.value.name) {
      const name = area.name || area.store_name || area.event_name || ''
      if (!name.toLowerCase().includes(filters.value.name.toLowerCase())) return false
    }

    // 按状态筛选
    if (filters.value.status === 'active' && !area.is_active) return false
    if (filters.value.status === 'inactive' && area.is_active) return false

    return true
  })
})

const paginatedAreas = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredAreas.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredAreas.value.length / pageSize.value)
})

// 方法
const loadData = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    // 1. 加载地图列表
    if (mapList.value.length === 0) {
      const mapsResponse = await listMaps()
      mapList.value = mapsResponse.data || mapsResponse
    }

    // 2. 根据筛选条件加载区域数据
    let data = []

    if (filters.value.type) {
      // 按类型加载
      data = await loadByType(filters.value.type)
    } else {
      // 加载所有类型
      const [stores, events, eventareas, others] = await Promise.all([
        loadStoreareas(),
        loadEvents(),
        loadEventareas(),
        loadOtherareas()
      ])
      data = [...stores, ...events, ...eventareas, ...others]
    }

    areas.value = data

  } catch (error) {
    console.error('加载数据失败:', error)
    errorMessage.value = `加载数据失败: ${error.message || '未知错误'}`
  } finally {
    loading.value = false
  }
}

const loadStoreareas = async () => {
  try {
    const response = await managementAPI.listManagementStoreareas()
    const storeareas = response.data || response
    return storeareas.map(item => ({ ...item, type: 'storearea' }))
  } catch (error) {
    console.error('加载店铺区域失败:', error)
    return []
  }
}

const loadEvents = async () => {
  try {
    const response = await managementAPI.listManagementEvents()
    const events = response.data || response
    return events.map(item => ({ ...item, type: 'event' }))
  } catch (error) {
    console.error('加载活动失败:', error)
    return []
  }
}

const loadEventareas = async () => {
  try {
    const response = await managementAPI.listManagementEventareas()
    const eventareas = response.data || response
    return eventareas.map(item => ({ ...item, type: 'eventarea' }))
  } catch (error) {
    console.error('加载活动区域失败:', error)
    return []
  }
}

const loadOtherareas = async () => {
  try {
    const response = await managementAPI.listManagementOtherareas()
    const otherareas = response.data || response
    return otherareas.map(item => ({ ...item, type: 'otherarea' }))
  } catch (error) {
    console.error('加载其他区域失败:', error)
    return []
  }
}

const loadByType = async (type) => {
  switch (type) {
    case 'storearea':
      return await loadStoreareas()
    case 'event':
      return await loadEvents()
    case 'eventarea':
      return await loadEventareas()
    case 'otherarea':
      return await loadOtherareas()
    default:
      return []
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  loadData()
}

const setStatus = (status) => {
  filters.value.status = status
  handleFilterChange()
}

const debounceSearch = () => {
  clearTimeout(debounceSearch.timer)
  debounceSearch.timer = setTimeout(handleFilterChange, 500)
}

const getTypeLabel = (area) => {
  const typeMap = {
    storearea: '店铺区域',
    eventarea: '活动区域',
    otherarea: '其他区域',
    event: '活动'
  }
  return typeMap[area.type] || area.type
}

const getTypeClass = (type) => {
  return type || 'storearea'
}

const getFormLabel = (field) => {
  const typeLabels = {
    storearea: { 名称: '店铺名称', 描述: '店铺描述' },
    eventarea: { 名称: '活动区域名称', 描述: '活动区域描述' },
    otherarea: { 名称: '其他区域名称', 描述: '其他区域描述' },
    event: { 名称: '活动名称', 描述: '活动描述' }
  }
  return typeLabels[formData.value.type]?.[field] || field
}

const onTypeChange = () => {
  // 重置表单字段
  formData.value = {
    id: null,
    type: formData.value.type,
    name: '',
    map_id: '',
    store_type: '0',
    type_id: '0',
    event_type: '0',
    description: '',
    is_active: true,
    logo_url: '',
    start_time: '',
    end_time: ''
  }
}

const getMapFloor = (mapId) => {
  const map = mapList.value.find(m => m.id === mapId)
  return map ? map.floor_number : '未知'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const handleCreate = () => {
  isEditing.value = false
  formData.value = {
    id: null,
    type: 'storearea',
    name: '',
    map_id: '',
    store_type: '0',
    type_id: '0',
    event_type: '0',
    description: '',
    is_active: true,
    logo_url: '',
    start_time: '',
    end_time: ''
  }
  errorMessage.value = ''
  showModal.value = true
}

const handleEdit = async (area) => {
  isEditing.value = true
  errorMessage.value = ''

  try {
    // 根据类型获取完整详情
    const response = await managementAPI.getAreaByTypeAndId(area.type, area.id)
    const areaData = response.data || response

    // 转换数据格式
    formData.value = {
      id: areaData.id,
      type: area.type,
      name: areaData.name || areaData.store_name || areaData.event_name || '',
      map_id: areaData.map_id || '',
      store_type: areaData.store_type?.toString() || '0',
      type_id: areaData.type_id?.toString() || '0',
      event_type: areaData.event_type?.toString() || '0',
      description: areaData.description || '',
      is_active: areaData.is_active !== undefined ? areaData.is_active : true,
      logo_url: areaData.logo_url || '',
      start_time: areaData.start_time || '',
      end_time: areaData.end_time || ''
    }

    showModal.value = true
  } catch (error) {
    console.error('获取详情失败:', error)
    errorMessage.value = `获取详情失败: ${error.message || '未知错误'}`
  }
}

const handleSubmit = async () => {
  errorMessage.value = ''
  submitting.value = true

  try {
    // 准备提交数据
    const submitData = { ...formData.value }

    // 移除前端添加的type字段（后端不需要）
    delete submitData.type

    // 根据不同类型设置正确的字段名
    if (formData.value.type === 'storearea') {
      submitData.store_name = submitData.name
      delete submitData.name
      submitData.store_type = parseInt(submitData.store_type)
    } else if (formData.value.type === 'event') {
      submitData.event_name = submitData.name
      delete submitData.name
      submitData.event_type = parseInt(submitData.event_type)
    } else if (formData.value.type === 'eventarea') {
      submitData.eventarea_type = parseInt(submitData.event_type)
      delete submitData.event_type
    } else if (formData.value.type === 'otherarea') {
      submitData.type = parseInt(submitData.type_id)
      delete submitData.type_id
    }

    if (isEditing.value) {
      // 更新数据
      await managementAPI.updateAreaByTypeAndId(formData.value.type, formData.value.id, submitData)
    } else {
      // 创建数据
      let response
      switch (formData.value.type) {
        case 'storearea':
          response = await managementAPI.createManagementStorearea(submitData)
          break
        case 'event':
          response = await managementAPI.createManagementEvent(submitData)
          break
        case 'eventarea':
          response = await managementAPI.createManagementEventarea(submitData)
          break
        case 'otherarea':
          response = await managementAPI.createManagementOtherarea(submitData)
          break
      }

      // 如果创建成功且需要创建对应的几何图形（在editor模块），可以在这里处理
      if (response && response.id && formData.value.type !== 'event') {
        // 可以提示用户需要在地图编辑器中创建几何图形
        console.log(`成功创建${getTypeLabel({ type: formData.value.type })}，ID: ${response.id}`)
      }
    }

    closeModal()
    loadData()
  } catch (error) {
    console.error('保存失败:', error)
    errorMessage.value = `保存失败: ${error.response?.data?.error || error.message || '未知错误'}`
  } finally {
    submitting.value = false
  }
}

const toggleStatus = async (area) => {
  try {
    const newStatus = !area.is_active
    await managementAPI.updateAreaByTypeAndId(area.type, area.id, { is_active: newStatus })
    area.is_active = newStatus
  } catch (error) {
    console.error('状态更新失败:', error)
    errorMessage.value = `状态更新失败: ${error.response?.data?.error || error.message || '未知错误'}`
  }
}

const handleViewOnMap = (area) => {
  if (area.type !== 'event') {
    // 跳转到地图编辑器并定位到该区域
    router.push({
      path: '/map-editor',
      query: { mapId: area.map_id, highlight: area.id, type: area.type }
    })
  } else {
    // 对于活动类型，可能没有地图关联
    alert('活动类型没有直接的地图关联，请查看活动详情')
  }
}

const closeModal = () => {
  if (!submitting.value) {
    showModal.value = false
    errorMessage.value = ''
  }
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.area-management {
  padding: 20px;
  background-color: #111827;
  min-height: 100vh;
  color: #f9fafb;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: #f9fafb;
}

.actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.2s;
  position: relative;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #f97316;
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background-color: #ea580c;
}

.btn-secondary {
  background-color: #374151;
  color: #d1d5db;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #4b5563;
}

.btn-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #ffffff;
  animation: spin 1s ease-in-out infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.filter-card {
  background-color: #1f2937;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid #374151;
}

.filter-row {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.filter-group {
  flex: 1;
  min-width: 200px;
}

.filter-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #9ca3af;
}

.filter-select {
  width: 100%;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #374151;
  background-color: #111827;
  color: #f9fafb;
  font-size: 14px;
}

.search-input-wrapper {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 8px 12px 8px 36px;
  border-radius: 4px;
  border: 1px solid #374151;
  background-color: #111827;
  color: #f9fafb;
  font-size: 14px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.status-buttons {
  display: flex;
  gap: 8px;
}

.status-btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid #374151;
  background-color: #111827;
  color: #d1d5db;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.status-btn.active {
  background-color: #f97316;
  border-color: #f97316;
  color: #ffffff;
}

.status-btn:hover:not(.active) {
  background-color: #374151;
}

.table-container {
  background-color: #1f2937;
  border-radius: 8px;
  border: 1px solid #374151;
  overflow: hidden;
}

.table-header {
  background-color: #374151;
}

.table-row {
  display: flex;
  padding: 16px 20px;
  border-bottom: 1px solid #374151;
}

.header-row {
  font-weight: 600;
  color: #d1d5db;
  background-color: #374151;
}

.table-cell {
  padding: 0 8px;
  display: flex;
  align-items: center;
}

.data-row:hover {
  background-color: #2d3748;
}

.area-name {
  font-weight: 500;
}

.type-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.type-badge.storearea {
  background-color: #3b82f6;
  color: #ffffff;
}

.type-badge.eventarea {
  background-color: #8b5cf6;
  color: #ffffff;
}

.type-badge.otherarea {
  background-color: #10b981;
  color: #ffffff;
}

.type-badge.event {
  background-color: #f59e0b;
  color: #ffffff;
}

.map-info {
  color: #60a5fa;
}

.text-muted {
  color: #9ca3af;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background-color: #10b98120;
  color: #10b981;
}

.status-badge.inactive {
  background-color: #ef444420;
  color: #ef4444;
}

.actions-cell {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 4px 8px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.edit-btn {
  background-color: #3b82f6;
  color: #ffffff;
}

.edit-btn:hover {
  background-color: #2563eb;
}

.view-btn {
  background-color: #8b5cf6;
  color: #ffffff;
}

.view-btn:hover {
  background-color: #7c3aed;
}

.activate-btn {
  background-color: #10b981;
  color: #ffffff;
}

.activate-btn:hover {
  background-color: #059669;
}

.deactivate-btn {
  background-color: #ef4444;
  color: #ffffff;
}

.deactivate-btn:hover {
  background-color: #dc2626;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #9ca3af;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #374151;
  border-top-color: #f97316;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #9ca3af;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding: 16px 0;
}

.pagination-info {
  color: #9ca3af;
  font-size: 14px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pagination-btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid #374151;
  background-color: #1f2937;
  color: #d1d5db;
  cursor: pointer;
  font-size: 13px;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn:not(:disabled):hover {
  background-color: #374151;
}

.pagination-current {
  color: #d1d5db;
  font-size: 14px;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #1f2937;
  border-radius: 8px;
  width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  border: 1px solid #374151;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #374151;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #f9fafb;
}

.modal-close {
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 24px;
  cursor: pointer;
  line-height: 1;
}

.modal-close:hover {
  color: #f9fafb;
}

.modal-body {
  padding: 20px;
}

.error-message {
  background-color: #ef444420;
  color: #ef4444;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 14px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  color: #d1d5db;
  font-size: 14px;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #374151;
  background-color: #111827;
  color: #f9fafb;
  font-size: 14px;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #f97316;
}

.form-textarea {
  resize: vertical;
}

.toggle-switch {
  display: flex;
  align-items: center;
}

.toggle-input {
  display: none;
}

.toggle-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 8px;
}

.toggle-slider {
  width: 44px;
  height: 24px;
  background-color: #374151;
  border-radius: 12px;
  position: relative;
  transition: background-color 0.2s;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  background-color: #f9fafb;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  transition: transform 0.2s;
}

.toggle-input:checked + .toggle-label .toggle-slider {
  background-color: #f97316;
}

.toggle-input:checked + .toggle-label .toggle-slider::before {
  transform: translateX(20px);
}

.toggle-text {
  color: #d1d5db;
  font-size: 14px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #374151;
}
</style>
