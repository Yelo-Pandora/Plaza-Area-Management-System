<!-- views/event-management/index.vue -->
<template>
  <div class="event-management">
    <div class="header">
      <h1 class="title">活动管理</h1>
      <div class="actions">
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-card">
      <div class="filter-row">
        <div class="filter-group">
          <label class="filter-label">活动类型</label>
          <select v-model="filters.type" class="filter-select" @change="handleFilterChange">
            <option value="">全部类型</option>
            <option v-for="type in eventTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label">状态筛选</label>
          <select v-model="filters.status" class="filter-select" @change="handleFilterChange">
            <option value="">全部状态</option>
            <option value="active">进行中</option>
            <option value="upcoming">即将开始</option>
            <option value="ended">已结束</option>
            <option value="inactive">已停用</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label">搜索名称</label>
          <div class="search-input-wrapper">
            <input
              v-model="filters.name"
              type="text"
              class="search-input"
              placeholder="输入活动名称..."
              @input="debounceSearch"
            >
            <span class="search-icon">🔍</span>
          </div>
        </div>
      </div>

      <div class="filter-row">
        <div class="filter-group">
          <label class="filter-label">时间范围</label>
          <div class="date-range">
            <input
              v-model="filters.startDate"
              type="date"
              class="date-input"
              @change="handleFilterChange"
            >
            <span class="date-separator">至</span>
            <input
              v-model="filters.endDate"
              type="date"
              class="date-input"
              @change="handleFilterChange"
            >
            <button v-if="filters.startDate || filters.endDate" class="date-clear-btn" @click="clearDateFilter">
              清空
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
          <div class="table-cell" style="flex: 2;">活动名称</div>
          <div class="table-cell" style="flex: 1;">类型</div>
          <div class="table-cell" style="flex: 1;">起始时间</div>
          <div class="table-cell" style="flex: 1;">结束时间</div>
          <div class="table-cell" style="flex: 0.8;">状态</div>
          <div class="table-cell" style="flex: 1.5;">操作</div>
        </div>
      </div>

      <div class="table-body">
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <span>加载中...</span>
        </div>

        <div v-else-if="events.length === 0" class="empty-state">
          <span class="empty-icon">📋</span>
          <p>暂无活动数据</p>
          <button class="btn btn-secondary" @click="handleCreate">创建第一个活动</button>
        </div>

        <div v-else>
          <div
            v-for="event in paginatedEvents"
            :key="event.id"
            class="table-row data-row"
          >
            <div class="table-cell" style="flex: 0.5;">{{ event.id }}</div>
            <div class="table-cell" style="flex: 2;">
              <div class="event-name-container">
                <span class="event-name">{{ event.event_name || '未命名' }}</span>
                <span v-if="event.description" class="event-description-tooltip" :title="event.description">
                  📝
                </span>
              </div>
            </div>
            <div class="table-cell" style="flex: 1;">
              <span :class="['type-badge', getTypeClass(event.event_type)]">
                {{ getTypeLabel(event.event_type) }}
              </span>
            </div>
            <div class="table-cell" style="flex: 1;">
              {{ formatDateTime(event.start_time) }}
            </div>
            <div class="table-cell" style="flex: 1;">
              {{ formatDateTime(event.end_time) }}
            </div>
            <div class="table-cell" style="flex: 0.8;">
              <span :class="['status-badge', getEventStatus(event)]">
                {{ getEventStatusText(event) }}
              </span>
            </div>
            <div class="table-cell actions-cell" style="flex: 1.5;">
              <button class="action-btn edit-btn" @click="handleEdit(event)">
                编辑
              </button>
              <button class="action-btn view-btn" @click="handleViewAreas(event)">
                关联区域
              </button>
              <button class="action-btn manage-btn" @click="handleManageOnMap(event)">
                地图管理
              </button>
              <button
                :class="['action-btn', event.is_active ? 'deactivate-btn' : 'activate-btn']"
                @click="toggleStatus(event)"
              >
                {{ event.is_active ? '停用' : '启用' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="events.length > 0" class="pagination">
      <div class="pagination-info">
        显示 {{ (currentPage - 1) * pageSize + 1 }} -
        {{ Math.min(currentPage * pageSize, events.length) }} 条，共 {{ events.length }} 条
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
          <h3 class="modal-title">{{ isEditing ? '编辑活动' : '创建活动' }}</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </div>

            <div class="form-group">
              <label class="form-label">活动名称</label>
              <input
                v-model="formData.event_name"
                type="text"
                class="form-input"
                placeholder="请输入活动名称"
                required
              >
            </div>

            <div class="form-group">
              <label class="form-label">活动类型</label>
              <select v-model="formData.event_type" class="form-select" required>
                <option v-for="type in eventTypes" :key="type.value" :value="type.value">
                  {{ type.label }}
                </option>
              </select>
            </div>

            <div class="form-row">
              <div class="form-group half">
                <label class="form-label">开始时间</label>
                <input
                  v-model="formData.start_time"
                  type="datetime-local"
                  class="form-input"
                  placeholder="请选择开始时间"
                  required
                >
              </div>
              <div class="form-group half">
                <label class="form-label">结束时间</label>
                <input
                  v-model="formData.end_time"
                  type="datetime-local"
                  class="form-input"
                  placeholder="请选择结束时间"
                  required
                >
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">活动描述</label>
              <textarea
                v-model="formData.description"
                class="form-textarea"
                rows="4"
                placeholder="请输入活动描述（可选）"
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

            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="closeModal" :disabled="submitting">
                取消
              </button>
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting" class="btn-spinner"></span>
                {{ isEditing ? '保存更改' : '创建活动' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 关联区域弹窗 -->
    <div v-if="showAreasModal" class="modal-overlay" @click="closeAreasModal">
      <div class="modal-content wide-modal" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">管理关联区域 - {{ currentEvent?.event_name }}</h3>
          <button class="modal-close" @click="closeAreasModal">×</button>
        </div>
        <div class="modal-body">
          <div v-if="loadingAreas" class="loading-container">
            <div class="loading-spinner"></div>
            <span>加载关联区域中...</span>
          </div>

          <div v-else>
            <div class="tabs">
              <button
                :class="['tab-btn', activeTab === 'storeareas' ? 'active' : '']"
                @click="activeTab = 'storeareas'"
              >
                店铺区域 ({{ storeareas.length }})
              </button>
              <button
                :class="['tab-btn', activeTab === 'eventareas' ? 'active' : '']"
                @click="activeTab = 'eventareas'"
              >
                活动区域 ({{ eventareas.length }})
              </button>
            </div>

            <div class="areas-list">
              <div v-if="activeTab === 'storeareas'" class="tab-content">
                <div v-if="storeareas.length === 0" class="empty-list">
                  暂无关联的店铺区域
                </div>
                <div v-else>
                  <div v-for="area in storeareas" :key="area.id" class="area-item">
                    <div class="area-info">
                      <span class="area-name">{{ area.store_name || area.name || '未命名' }}</span>
                      <span class="area-type">店铺区域</span>
                    </div>
                    <button class="btn btn-danger btn-sm" @click="removeStoreareaFromEvent(area.id)">
                      移除
                    </button>
                  </div>
                </div>

                <div class="add-area-section">
                  <h4>添加店铺区域</h4>
                  <div class="search-area">
                    <input
                      v-model="storeareaSearch"
                      type="text"
                      class="search-input"
                      placeholder="搜索店铺区域..."
                      @input="searchStoreareas"
                    >
                  </div>
                  <div v-if="searchResults.length > 0" class="search-results">
                    <div v-for="area in searchResults" :key="area.id" class="search-result-item">
                      <div class="result-info">
                        <span class="result-name">{{ area.store_name || area.name || '未命名' }}</span>
                        <span class="result-type">店铺区域</span>
                      </div>
                      <button
                        class="btn btn-success btn-sm"
                        @click="addStoreareaToEvent(area.id)"
                        :disabled="isStoreareaLinked(area.id)"
                      >
                        {{ isStoreareaLinked(area.id) ? '已关联' : '添加' }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="activeTab === 'eventareas'" class="tab-content">
                <div v-if="eventareas.length === 0" class="empty-list">
                  暂无关联的活动区域
                </div>
                <div v-else>
                  <div v-for="area in eventareas" :key="area.id" class="area-item">
                    <div class="area-info">
                      <span class="area-name">{{ area.name || '未命名' }}</span>
                      <span class="area-type">活动区域</span>
                    </div>
                    <button class="btn btn-danger btn-sm" @click="removeEventareaFromEvent(area.id)">
                      移除
                    </button>
                  </div>
                </div>

                <div class="add-area-section">
                  <h4>添加活动区域</h4>
                  <div class="search-area">
                    <input
                      v-model="eventareaSearch"
                      type="text"
                      class="search-input"
                      placeholder="搜索活动区域..."
                      @input="searchEventareas"
                    >
                  </div>
                  <div v-if="eventareaResults.length > 0" class="search-results">
                    <div v-for="area in eventareaResults" :key="area.id" class="search-result-item">
                      <div class="result-info">
                        <span class="result-name">{{ area.name || '未命名' }}</span>
                        <span class="result-type">活动区域</span>
                      </div>
                      <button
                        class="btn btn-success btn-sm"
                        @click="addEventareaToEvent(area.id)"
                        :disabled="isEventareaLinked(area.id)"
                      >
                        {{ isEventareaLinked(area.id) ? '已关联' : '添加' }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as managementAPI from '../../api/management'
import * as searchAPI from '../../api/search'
import * as editorAPI from '../../api/editor'

const router = useRouter()

// 数据状态
const events = ref([])
const loading = ref(true)
const errorMessage = ref('')
const submitting = ref(false)

// 关联区域相关状态
const showAreasModal = ref(false)
const currentEvent = ref(null)
const loadingAreas = ref(false)
const storeareas = ref([])
const eventareas = ref([])
const activeTab = ref('storeareas')
const storeareaSearch = ref('')
const eventareaSearch = ref('')
const searchResults = ref([])
const eventareaResults = ref([])

// 筛选条件
const filters = ref({
  type: '',
  status: '',
  name: '',
  startDate: '',
  endDate: ''
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 弹窗状态
const showModal = ref(false)
const isEditing = ref(false)
const formData = ref({
  id: null,
  event_name: '',
  event_type: '0',
  start_time: '',
  end_time: '',
  description: '',
  organizer: '',
  location: '',
  is_active: true
})

// 活动类型配置
const eventTypes = [
  { value: '0', label: '普通活动' },
  { value: '1', label: '促销活动' },
  { value: '2', label: '展览活动' },
  { value: '3', label: '表演活动' },
  { value: '4', label: '节日活动' },
  { value: '5', label: '体验活动' }
]

// 计算属性
const filteredEvents = computed(() => {
  // const now = new Date()

  return events.value.filter(event => {
    // 按类型筛选
    if (filters.value.type && event.event_type.toString() !== filters.value.type) return false

    // 按名称搜索
    if (filters.value.name) {
      const name = event.event_name || ''
      if (!name.toLowerCase().includes(filters.value.name.toLowerCase())) return false
    }

    // 按状态筛选
    if (filters.value.status) {
      const status = getEventStatus(event)
      if (status !== filters.value.status) return false
    }

    // 按时间范围筛选
    if (filters.value.startDate) {
      // 使用字符串比较日期部分
      const eventDatePart = event.start_time?.substring(0, 10) || ''
      if (eventDatePart < filters.value.startDate) return false
    }

    if (filters.value.endDate) {
      // 使用字符串比较日期部分
      const eventDatePart = event.end_time?.substring(0, 10) || ''
      if (eventDatePart > filters.value.endDate) return false
    }

    return true
  })
})

const paginatedEvents = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredEvents.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredEvents.value.length / pageSize.value)
})

// 方法
const loadData = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await managementAPI.listManagementEvents()
    events.value = response.data || response

    // 确保数据有正确的字段
    events.value = events.value.map(event => ({
      ...event,
      // ⭐ 字段映射（关键）
      start_time: event.start_time ?? event.start_date,
      end_time: event.end_time ?? event.end_date,
      event_type: event.event_type ?? '0',
      is_active: event.is_active !== undefined ? event.is_active : true
    }))

  } catch (error) {
    console.error('加载活动数据失败:', error)
    errorMessage.value = `加载数据失败: ${error.message || '未知错误'}`
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
}

const debounceSearch = () => {
  clearTimeout(debounceSearch.timer)
  debounceSearch.timer = setTimeout(handleFilterChange, 500)
}

const clearDateFilter = () => {
  filters.value.startDate = ''
  filters.value.endDate = ''
  handleFilterChange()
}

const getTypeLabel = (type) => {
  const typeObj = eventTypes.find(t => t.value === type.toString())
  return typeObj ? typeObj.label : `类型${type}`
}

const getTypeClass = (type) => {
  const typeClasses = {
    '0': 'normal',
    '1': 'promotion',
    '2': 'exhibition',
    '3': 'performance',
    '4': 'festival',
    '5': 'experience'
  }
  return typeClasses[type] || 'normal'
}

const getEventStatus = (event) => {
  const now = new Date()
  const startTime = parseBackendDateTime(event.start_time)
  const endTime = parseBackendDateTime(event.end_time)

  // 如果活动本身是停用状态，直接返回inactive
  if (!event.is_active) return 'inactive'

  // 如果时间解析成功，根据时间判断状态
  if (startTime && endTime) {
    if (now < startTime) return 'upcoming'
    if (now > endTime) return 'ended'
    return 'active'
  }

  // 如果时间解析失败，但活动是启用状态，返回active作为默认状态
  return 'active'
}

const getEventStatusText = (event) => {
  const status = getEventStatus(event)
  const statusMap = {
    'active': '进行中',
    'upcoming': '即将开始',
    'ended': '已结束',
    'inactive': '已停用'
  }
  return statusMap[status] || '未知'
}

const parseBackendDateTime = (dateString) => {
  if (!dateString) return null

  try {
    let normalized = dateString

    // 1️⃣ PostgreSQL: 2025-12-23 04:27:42.443939
    normalized = normalized.replace(' ', 'T')

    // 2️⃣ 移除多余微秒（保留毫秒）
    normalized = normalized.replace(/\.(\d{3})\d+/, '.$1')

    // 3️⃣ 如果没有时区，默认当作本地时间
    const date = new Date(normalized)

    return isNaN(date.getTime()) ? null : date
  } catch (error) {
    console.error('日期解析错误:', error, '原始字符串:', dateString)
    return null
  }
};

// 将后端日期时间字符串转换为前端datetime-local格式
const backendToDateTimeLocal = (dateString) => {
  if (!dateString) return ''

  // "2025-12-23 04:27:42" → "2025-12-23T04:27"
  return dateString.replace(' ', 'T').slice(0, 16)
};

// 将前端datetime-local格式转换为后端格式
const dateTimeLocalToBackend = (localValue) => {
  if (!localValue) return null

  // "2025-12-23T04:27" → "2025-12-23 04:27:00"
  return localValue.replace('T', ' ') + ':00'
};



const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = parseBackendDateTime(dateString)
  return date ? date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }) : '-'
}

const handleCreate = () => {
  isEditing.value = false
  const now = new Date()
  const tomorrow = new Date(now)
  tomorrow.setDate(tomorrow.getDate() + 1)

  // 将日期转换为本地时间格式
  const toLocalInput = (date) =>
    new Date(date.getTime() - date.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 16)

  formData.value = {
    id: null,
    event_name: '',
    event_type: '0',
    start_time: toLocalInput(now),
    end_time: toLocalInput(tomorrow),
    description: '',
    organizer: '',
    location: '',
    is_active: true
  }
  errorMessage.value = ''
  showModal.value = true
}

const handleEdit = async (event) => {
  isEditing.value = true
  errorMessage.value = ''

  try {
    const response = await managementAPI.getManagementEvent(event.id)
    const eventData = response.data || response

    formData.value = {
      id: eventData.id,
      event_name: eventData.event_name || '',
      event_type: eventData.event_type?.toString() || '0',
      start_time: backendToDateTimeLocal(eventData.start_time ?? eventData.start_date),
      end_time: backendToDateTimeLocal(eventData.end_time ?? eventData.end_date),
      description: eventData.description || '',
      organizer: eventData.organizer || '',
      location: eventData.location || '',
      is_active: eventData.is_active ?? true
    }

    showModal.value = true
  } catch (error) {
    console.error('获取活动详情失败:', error)
    errorMessage.value = `获取详情失败: ${error.message || '未知错误'}`
  }
}

const handleSubmit = async () => {
  errorMessage.value = ''
  submitting.value = true

  try {
    const submitData = { ...formData.value }


    // 验证时间
    const startTime = new Date(submitData.start_time)
    const endTime = new Date(submitData.end_time)

    if (endTime <= startTime) {
      throw new Error('结束时间必须晚于开始时间')
    }

    // 转换时间格式
  submitData.start_time = dateTimeLocalToBackend(submitData.start_time)
  submitData.end_time = dateTimeLocalToBackend(submitData.end_time)

    // 移除id字段（如果是创建）
    const id = submitData.id
    if (!isEditing.value) {
      delete submitData.id
    }

    // 转换event_type为数字
    submitData.event_type = parseInt(submitData.event_type)

    if (isEditing.value) {
      // 更新活动 - 映射字段名
      const payload = {
        ...submitData,
        start_date: submitData.start_time,
        end_date: submitData.end_time
      }
      delete payload.start_time
      delete payload.end_time

      await managementAPI.updateManagementEvent(id, payload)
    } else {
      // 创建活动 - 映射字段名
      const payload = {
        ...submitData,
        start_date: submitData.start_time,
        end_date: submitData.end_time
      }
      delete payload.start_time
      delete payload.end_time

      await managementAPI.createManagementEvent(payload)
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

const toggleStatus = async (event) => {
  try {
    const newStatus = !event.is_active
    await managementAPI.partialUpdateManagementEvent(event.id, { is_active: newStatus })
    event.is_active = newStatus
  } catch (error) {
    console.error('状态更新失败:', error)
    errorMessage.value = `状态更新失败: ${error.response?.data?.error || error.message || '未知错误'}`
  }
}

const handleViewAreas = async (event) => {
  currentEvent.value = event
  loadingAreas.value = true
  showAreasModal.value = true

  try {
    // 加载关联的区域
    await loadEventAreas(event.id)
  } catch (error) {
    console.error('加载关联区域失败:', error)
    errorMessage.value = `加载关联区域失败: ${error.message || '未知错误'}`
  } finally {
    loadingAreas.value = false
  }
}

const handleManageOnMap = (event) => {
  // 跳转到地图编辑器，可以管理活动相关的区域
  router.push({
    path: '/map-editor',
    query: {
      mode: 'event',
      eventId: event.id,
      eventName: event.event_name
    }
  })
}

const loadEventAreas = async (eventId) => {
  try {
    // 从editor模块获取关联的区域
    const response = await editorAPI.getEventAreasForEditor(eventId)
    const data = response.data || response

    // 获取店铺区域详情
    const storeareaPromises = (data.storearea_ids || []).map(id =>
      managementAPI.getManagementStorearea(id).catch(() => null)
    )

    // 获取活动区域详情
    const eventareaPromises = (data.eventarea_ids || []).map(id =>
      managementAPI.getManagementEventarea(id).catch(() => null)
    )

    const [storeareaResults, eventareaResults] = await Promise.all([
      Promise.all(storeareaPromises),
      Promise.all(eventareaPromises)
    ])

    storeareas.value = storeareaResults.filter(r => r).map(r => r.data || r)
    eventareas.value = eventareaResults.filter(r => r).map(r => r.data || r)

  } catch (error) {
    console.error('加载事件区域失败:', error)
    throw error
  }
}

const searchStoreareas = async () => {
  if (!storeareaSearch.value.trim()) {
    searchResults.value = []
    return
  }

  try {
    const response = await searchAPI.searchStoreareaByName(storeareaSearch.value)
    searchResults.value = response.data || response
  } catch (error) {
    console.error('搜索店铺区域失败:', error)
    searchResults.value = []
  }
}

const searchEventareas = async () => {
  if (!eventareaSearch.value.trim()) {
    eventareaResults.value = []
    return
  }

  try {
    const response = await managementAPI.listManagementEventareas()
    const allEventareas = response.data || response
    eventareaResults.value = allEventareas.filter(area =>
      (area.name || '').toLowerCase().includes(eventareaSearch.value.toLowerCase())
    )
  } catch (error) {
    console.error('搜索活动区域失败:', error)
    eventareaResults.value = []
  }
}

const isStoreareaLinked = (areaId) => {
  return storeareas.value.some(area => area.id === areaId)
}

const isEventareaLinked = (areaId) => {
  return eventareas.value.some(area => area.id === areaId)
}

const addStoreareaToEvent = async (storeareaId) => {
  try {
    await editorAPI.addStoreareaToEvent(currentEvent.value.id, storeareaId)

    // 重新加载关联区域
    await loadEventAreas(currentEvent.value.id)

    // 清空搜索结果
    searchResults.value = []
    storeareaSearch.value = ''
  } catch (error) {
    console.error('添加店铺区域失败:', error)
    errorMessage.value = `添加失败: ${error.response?.data?.error || error.message || '未知错误'}`
  }
}

const removeStoreareaFromEvent = async (storeareaId) => {
  try {
    await editorAPI.removeStoreareaFromEvent(currentEvent.value.id, storeareaId)

    // 重新加载关联区域
    await loadEventAreas(currentEvent.value.id)
  } catch (error) {
    console.error('移除店铺区域失败:', error)
    errorMessage.value = `移除失败: ${error.response?.data?.error || error.message || '未知错误'}`
  }
}

const addEventareaToEvent = async (eventareaId) => {
  try {
    await editorAPI.addEventareaToEvent(currentEvent.value.id, eventareaId)

    // 重新加载关联区域
    await loadEventAreas(currentEvent.value.id)

    // 清空搜索结果
    eventareaResults.value = []
    eventareaSearch.value = ''
  } catch (error) {
    console.error('添加活动区域失败:', error)
    errorMessage.value = `添加失败: ${error.response?.data?.error || error.message || '未知错误'}`
  }
}

const removeEventareaFromEvent = async (eventareaId) => {
  try {
    await editorAPI.removeEventareaFromEvent(currentEvent.value.id, eventareaId)

    // 重新加载关联区域
    await loadEventAreas(currentEvent.value.id)
  } catch (error) {
    console.error('移除活动区域失败:', error)
    errorMessage.value = `移除失败: ${error.response?.data?.error || error.message || '未知错误'}`
  }
}

const closeModal = () => {
  if (!submitting.value) {
    showModal.value = false
    errorMessage.value = ''
  }
}

const closeAreasModal = () => {
  showAreasModal.value = false
  currentEvent.value = null
  storeareas.value = []
  eventareas.value = []
  activeTab.value = 'storeareas'
  storeareaSearch.value = ''
  eventareaSearch.value = ''
  searchResults.value = []
  eventareaResults.value = []
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.event-management {
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

.btn-success {
  background-color: #10b981;
  color: #ffffff;
}

.btn-success:hover:not(:disabled) {
  background-color: #059669;
}

.btn-danger {
  background-color: #ef4444;
  color: #ffffff;
}

.btn-danger:hover:not(:disabled) {
  background-color: #dc2626;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
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

.date-range {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.date-input {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #374151;
  background-color: #111827;
  color: #f9fafb;
  font-size: 14px;
  flex: 1;
}

.date-separator {
  color: #9ca3af;
  font-size: 14px;
}

.date-clear-btn {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #374151;
  background-color: #111827;
  color: #d1d5db;
  cursor: pointer;
  font-size: 13px;
}

.date-clear-btn:hover {
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

.event-name-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.event-name {
  font-weight: 500;
}

.event-description-tooltip {
  color: #9ca3af;
  cursor: help;
  font-size: 14px;
}

.type-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.type-badge.normal {
  background-color: #3b82f6;
  color: #ffffff;
}

.type-badge.promotion {
  background-color: #f59e0b;
  color: #ffffff;
}

.type-badge.exhibition {
  background-color: #8b5cf6;
  color: #ffffff;
}

.type-badge.performance {
  background-color: #ec4899;
  color: #ffffff;
}

.type-badge.festival {
  background-color: #10b981;
  color: #ffffff;
}

.type-badge.experience {
  background-color: #ef4444;
  color: #ffffff;
}

.time-range {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 13px;
}

.time-to {
  color: #9ca3af;
  font-size: 11px;
  text-align: center;
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

.status-badge.upcoming {
  background-color: #f59e0b20;
  color: #f59e0b;
}

.status-badge.ended {
  background-color: #6b728020;
  color: #9ca3af;
}

.status-badge.inactive {
  background-color: #ef444420;
  color: #ef4444;
}

.actions-cell {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 4px 8px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: background-color 0.2s;
  white-space: nowrap;
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

.manage-btn {
  background-color: #f59e0b;
  color: #ffffff;
}

.manage-btn:hover {
  background-color: #d97706;
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
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state .btn {
  margin-top: 16px;
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

.wide-modal {
  width: 700px;
  max-width: 95vw;
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

.form-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.form-row .form-group {
  flex: 1;
  margin-bottom: 0;
}

.half {
  flex: 0.5;
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

/* 关联区域弹窗样式 */
.tabs {
  display: flex;
  border-bottom: 1px solid #374151;
  margin-bottom: 20px;
}

.tab-btn {
  padding: 10px 20px;
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #d1d5db;
}

.tab-btn.active {
  color: #f97316;
  border-bottom-color: #f97316;
}

.areas-list {
  max-height: 400px;
  overflow-y: auto;
}

.empty-list {
  text-align: center;
  padding: 30px;
  color: #9ca3af;
  font-size: 14px;
}

.area-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #374151;
  border-radius: 4px;
  margin-bottom: 8px;
  background-color: #111827;
}

.area-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.area-name {
  font-weight: 500;
  color: #f9fafb;
}

.area-type {
  font-size: 12px;
  color: #9ca3af;
}

.add-area-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #374151;
}

.add-area-section h4 {
  margin-bottom: 12px;
  color: #f9fafb;
  font-size: 16px;
}

.search-area {
  margin-bottom: 16px;
}

.search-results {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #374151;
  border-radius: 4px;
}

.search-result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid #374151;
}

.search-result-item:last-child {
  border-bottom: none;
}

.result-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.result-name {
  color: #f9fafb;
  font-size: 14px;
}

.result-type {
  font-size: 12px;
  color: #9ca3af;
}
</style>
