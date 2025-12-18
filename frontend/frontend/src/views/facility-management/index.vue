<!-- views/facility-management/index.vue -->
<template>
  <div class="facility-management">
    <div class="header">
      <h1 class="title">设施管理</h1>
      <div class="actions">
        <button class="btn btn-primary" @click="handleCreate">
          <span class="btn-icon">+</span> 新建设施
        </button>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-card">
      <div class="filter-row">
        <div class="filter-group">
          <label class="filter-label">设施类型</label>
          <select v-model="filters.type" class="filter-select" @change="handleFilterChange">
            <option value="">全部类型</option>
            <option value="0">电梯</option>
            <option value="1">卫生间</option>
            <option value="2">安全出口</option>
            <option value="3">服务台</option>
            <option value="4">其他</option>
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
              placeholder="输入设施名称..."
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

        <div v-else-if="facilities.length === 0" class="empty-state">
          <span class="empty-icon">📋</span>
          <p>暂无设施数据</p>
        </div>

        <div v-else>
          <div
            v-for="facility in paginatedFacilities"
            :key="facility.id"
            class="table-row data-row"
          >
            <div class="table-cell" style="flex: 0.5;">{{ facility.id }}</div>
            <div class="table-cell" style="flex: 1.5;">
              <span class="facility-name">{{ facility.description || '未命名' }}</span>
            </div>
            <div class="table-cell" style="flex: 1;">
              <span :class="['type-badge', getTypeClass(facility.type)]">
                {{ getTypeLabel(facility.type) }}
              </span>
            </div>
            <div class="table-cell" style="flex: 1;">
              <span v-if="facility.map_id" class="map-info">
                楼层 {{ getMapFloor(facility.map_id) }}
              </span>
              <span v-else class="text-muted">未分配</span>
            </div>
            <div class="table-cell" style="flex: 0.8;">
              <span :class="['status-badge', facility.is_active ? 'active' : 'inactive']">
                {{ facility.is_active ? '启用' : '停用' }}
              </span>
            </div>
            <div class="table-cell" style="flex: 1.5;">
              {{ formatDate(facility.created_at) }}
            </div>
            <div class="table-cell actions-cell" style="flex: 1.2;">
              <button class="action-btn edit-btn" @click="handleEdit(facility)">
                编辑
              </button>
              <button class="action-btn view-btn" @click="handleViewOnMap(facility)">
                查看
              </button>
              <button
                :class="['action-btn', facility.is_active ? 'deactivate-btn' : 'activate-btn']"
                @click="toggleStatus(facility)"
              >
                {{ facility.is_active ? '停用' : '启用' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="facilities.length > 0" class="pagination">
      <div class="pagination-info">
        显示 {{ (currentPage - 1) * pageSize + 1 }} -
        {{ Math.min(currentPage * pageSize, facilities.length) }} 条，共 {{ facilities.length }} 条
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
          <h3 class="modal-title">{{ isEditing ? '编辑设施' : '创建设施' }}</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </div>

            <div class="form-group">
              <label class="form-label">设施名称</label>
              <input
                v-model="formData.description"
                type="text"
                class="form-input"
                placeholder="请输入设施名称"
                required
              >
            </div>

            <div class="form-group">
              <label class="form-label">设施类型</label>
              <select v-model="formData.type" class="form-select">
                <option value="0">电梯</option>
                <option value="1">卫生间</option>
                <option value="2">安全出口</option>
                <option value="3">服务台</option>
                <option value="4">其他</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">所属地图</label>
              <select v-model="formData.map_id" class="form-select" required>
                <option value="">请选择地图楼层</option>
                <option v-for="map in mapList" :key="map.id" :value="map.id">
                  楼层 {{ map.floor_number }}
                </option>
              </select>
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
                {{ isEditing ? '保存更改' : '创建设施' }}
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

const router = useRouter()

// 数据状态
const facilities = ref([])
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
  type: '0',
  description: '',
  map_id: '',
  is_active: true
})

// 计算属性
const filteredFacilities = computed(() => {
  return facilities.value.filter(facility => {
    // 按类型筛选
    if (filters.value.type && facility.type !== parseInt(filters.value.type)) return false

    // 按地图筛选
    if (filters.value.map_id && facility.map_id !== parseInt(filters.value.map_id)) return false

    // 按名称搜索
    if (filters.value.name) {
      const name = facility.description || ''
      if (!name.toLowerCase().includes(filters.value.name.toLowerCase())) return false
    }

    // 按状态筛选
    if (filters.value.status === 'active' && !facility.is_active) return false
    if (filters.value.status === 'inactive' && facility.is_active) return false

    return true
  })
})

const paginatedFacilities = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredFacilities.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredFacilities.value.length / pageSize.value)
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

    // 2. 加载设施数据
    const response = await managementAPI.listManagementFacilities()
    facilities.value = response.data || response

  } catch (error) {
    console.error('加载数据失败:', error)
    errorMessage.value = `加载数据失败: ${error.message || '未知错误'}`
  } finally {
    loading.value = false
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

const getTypeLabel = (type) => {
  const typeMap = {
    0: '电梯',
    1: '卫生间',
    2: '安全出口',
    3: '服务台',
    4: '其他'
  }
  return typeMap[type] || '其他'
}

const getTypeClass = (type) => {
  return `type-${type || 4}`
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
    type: '0',
    description: '',
    map_id: '',
    is_active: true
  }
  errorMessage.value = ''
  showModal.value = true
}

const handleEdit = async (facility) => {
  isEditing.value = true
  errorMessage.value = ''

  try {
    // 获取完整详情
    const response = await managementAPI.getManagementFacility(facility.id)
    const facilityData = response.data || response

    // 转换数据格式
    formData.value = {
      id: facilityData.id,
      type: facilityData.type?.toString() || '0',
      description: facilityData.description || '',
      map_id: facilityData.map_id || '',
      is_active: facilityData.is_active !== undefined ? facilityData.is_active : true
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
    const submitData = {
      type: parseInt(formData.value.type),
      description: formData.value.description,
      map_id: parseInt(formData.value.map_id),
      is_active: formData.value.is_active
    }

    if (isEditing.value) {
      // 更新
      await managementAPI.updateManagementFacility(formData.value.id, submitData)
    } else {
      // 创建
      await managementAPI.createManagementFacility(submitData)
    }

    // 关闭弹窗并刷新数据
    closeModal()
    loadData()
  } catch (error) {
    console.error('提交失败:', error)
    errorMessage.value = `提交失败: ${error.response?.data?.error || error.message || '未知错误'}`
  } finally {
    submitting.value = false
  }
}

const toggleStatus = async (facility) => {
  try {
    // 更新状态
    await managementAPI.partialUpdateManagementFacility(facility.id, {
      is_active: !facility.is_active
    })

    // 刷新数据
    loadData()
  } catch (error) {
    console.error('更新状态失败:', error)
    errorMessage.value = `更新状态失败: ${error.message || '未知错误'}`
  }
}

const handleViewOnMap = (facility) => {
  // 跳转到地图编辑器并选中该设施
  router.push({
    path: '/map-editor',
    query: {
      facilityId: facility.id,
      mapId: facility.map_id
    }
  })
}

const closeModal = () => {
  if (!submitting.value) {
    showModal.value = false
    errorMessage.value = ''
  }
}

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.facility-management {
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

.filter-select:focus {
  outline: none;
  border-color: #f97316;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  width: 100%;
  padding: 8px 12px 8px 36px;
  border: 1px solid #374151;
  border-radius: 4px;
  font-size: 14px;
  background-color: #111827;
  color: #f9fafb;
}

.search-input:focus {
  outline: none;
  border-color: #f97316;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
  font-size: 16px;
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
  font-size: 14px;
  color: #d1d5db;
}

.data-row:hover {
  background-color: #2d3748;
}

.facility-name {
  font-weight: 500;
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

.type-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  color: white;
}

.type-0 {
  background-color: #2563eb;
}

.type-1 {
  background-color: #10b981;
}

.type-2 {
  background-color: #ef4444;
}

.type-3 {
  background-color: #f59e0b;
}

.type-4 {
  background-color: #8b5cf6;
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

.text-muted {
  color: #9ca3af;
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

.deactivate-btn {
  background-color: #ef4444;
  color: #ffffff;
}

.deactivate-btn:hover {
  background-color: #dc2626;
}

.activate-btn {
  background-color: #10b981;
  color: #ffffff;
}

.activate-btn:hover {
  background-color: #059669;
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
.form-select {
  width: 100%;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #374151;
  background-color: #111827;
  color: #f9fafb;
  font-size: 14px;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #f97316;
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
  background-color: #10b981;
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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: #1f2937;
  border-radius: 8px;
  max-width: 500px;
  width: 100%;
  margin: 1rem;
  border: 1px solid #374151;
  max-height: 90vh;
  overflow-y: auto;
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
  font-size: 24px;
  color: #9ca3af;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s ease;
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
  font-size: 14px;
  font-weight: 500;
  color: #d1d5db;
}

.form-input, .form-select, .form-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #374151;
  border-radius: 4px;
  font-size: 14px;
  background-color: #111827;
  color: #f9fafb;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: #f97316;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.toggle-switch {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-input {
  display: none;
}

.toggle-label {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.toggle-slider {
  width: 44px;
  height: 24px;
  background-color: #374151;
  border-radius: 12px;
  transition: all 0.2s ease;
  position: relative;
}

.toggle-input:checked + .toggle-label .toggle-slider {
  background-color: #f97316;
}

.toggle-input:checked + .toggle-label .toggle-slider::before {
  transform: translateX(20px);
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
  transition: all 0.2s ease;
}

.toggle-text {
  font-size: 14px;
  color: #d1d5db;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #374151;
}

.btn-secondary {
  background-color: #374151;
  color: #d1d5db;
  border: 1px solid #4b5563;
}

.btn-secondary:hover {
  background-color: #4b5563;
}

.btn-spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
</style>