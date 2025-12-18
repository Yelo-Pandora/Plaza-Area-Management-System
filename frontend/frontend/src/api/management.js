import { request } from './index'

/**
 * Management 模块：负责非几何属性的CRUD和管理员认证
 * 前缀：/api/management/
 *
 * 约定：
 * - 在 management 模块中，只处理非几何属性（不允许修改shape）
 * - shape 字段的创建/更新由 editor 模块处理
 * - 创建/更新时若包含shape字段，后端会自动移除或返回错误
 */

// ---------- 管理员认证与个人信息 ----------

/**
 * 管理员注册
 * @param {Object} adminData - 管理员注册数据
 * @returns {Promise}
 */
export function adminRegister(adminData) {
  return request('api/management/auth/register/', {
    method: 'POST',
    body: adminData
  })
}

/**
 * 管理员登录
 * @param {Object} credentials - 登录凭据 {account, password}
 * @returns {Promise}
 */
export function adminLogin(credentials) {
  return request('api/management/auth/login/', {
    method: 'POST',
    body: credentials
  })
}

/**
 * 管理员注销
 * @returns {Promise}
 */
export function adminLogout() {
  return request('api/management/auth/logout/', {
    method: 'POST'
  })
}

/**
 * 获取当前登录管理员个人信息
 * @returns {Promise}
 */
export function getAdminProfile() {
  return request('api/management/profile/', {
    method: 'GET'
  })
}

/**
 * 更新当前登录管理员个人信息
 * @param {Object} profileData - 更新的个人信息
 * @returns {Promise}
 */
export function updateAdminProfile(profileData) {
  return request('api/management/profile/', {
    method: 'PUT',
    body: profileData
  })
}

// ---------- 活动区域（Eventarea）管理 ----------

/**
 * 获取所有活动区域列表
 * @returns {Promise}
 */
export function listManagementEventareas() {
  return request('api/management/eventarea/', {
    method: 'GET'
  })
}

/**
 * 获取指定活动区域详情
 * @param {number} id - 活动区域ID
 * @returns {Promise}
 */
export function getManagementEventarea(id) {
  return request(`api/management/eventarea/${id}/`, {
    method: 'GET'
  })
}

/**
 * 创建新的活动区域（自动移除shape字段）
 * @param {Object} eventareaData - 活动区域数据（不含shape）
 * @returns {Promise}
 */
export function createManagementEventarea(eventareaData) {
  // 确保不包含shape字段
  const data = { ...eventareaData }
  if ('shape' in data) {
    console.warn('Warning: shape字段将在management.create中被自动移除')
    delete data.shape
  }

  return request('api/management/eventarea/', {
    method: 'POST',
    body: data
  })
}

/**
 * 完整更新活动区域（不允许更新shape）
 * @param {number} id - 活动区域ID
 * @param {Object} eventareaData - 完整更新数据（不含shape）
 * @returns {Promise}
 */
export function updateManagementEventarea(id, eventareaData) {
  // 检查是否包含shape字段，如果包含则拒绝
  if ('shape' in eventareaData) {
    return Promise.reject(new Error('Shape attribute cannot be updated in management module'))
  }

  return request(`api/management/eventarea/${id}/`, {
    method: 'PUT',
    body: eventareaData
  })
}

/**
 * 部分更新活动区域（不允许更新shape）
 * @param {number} id - 活动区域ID
 * @param {Object} eventareaData - 部分更新数据（不含shape）
 * @returns {Promise}
 */
export function partialUpdateManagementEventarea(id, eventareaData) {
  // 检查是否包含shape字段，如果包含则拒绝
  if ('shape' in eventareaData) {
    return Promise.reject(new Error('Shape attribute cannot be updated in management module'))
  }

  return request(`api/management/eventarea/${id}/`, {
    method: 'PATCH',
    body: eventareaData
  })
}

/**
 * 删除指定活动区域
 * @param {number} id - 活动区域ID
 * @returns {Promise}
 */
export function deleteManagementEventarea(id) {
  return request(`api/management/eventarea/${id}/`, {
    method: 'DELETE'
  })
}

// ---------- 其他区域（Otherarea）管理 ----------

/**
 * 获取所有其他区域列表
 * @returns {Promise}
 */
export function listManagementOtherareas() {
  return request('api/management/otherarea/', {
    method: 'GET'
  })
}

/**
 * 获取指定其他区域详情
 * @param {number} id - 其他区域ID
 * @returns {Promise}
 */
export function getManagementOtherarea(id) {
  return request(`api/management/otherarea/${id}/`, {
    method: 'GET'
  })
}

/**
 * 创建新的其他区域（自动移除shape字段）
 * @param {Object} otherareaData - 其他区域数据（不含shape）
 * @returns {Promise}
 */
export function createManagementOtherarea(otherareaData) {
  // 确保不包含shape字段
  const data = { ...otherareaData }
  if ('shape' in data) {
    console.warn('Warning: shape字段将在management.create中被自动移除')
    delete data.shape
  }

  return request('api/management/otherarea/', {
    method: 'POST',
    body: data
  })
}

/**
 * 完整更新其他区域（不允许更新shape）
 * @param {number} id - 其他区域ID
 * @param {Object} otherareaData - 完整更新数据（不含shape）
 * @returns {Promise}
 */
export function updateManagementOtherarea(id, otherareaData) {
  // 检查是否包含shape字段，如果包含则拒绝
  if ('shape' in otherareaData) {
    return Promise.reject(new Error('Shape attribute cannot be updated in management module'))
  }

  return request(`api/management/otherarea/${id}/`, {
    method: 'PUT',
    body: otherareaData
  })
}

/**
 * 部分更新其他区域（不允许更新shape）
 * @param {number} id - 其他区域ID
 * @param {Object} otherareaData - 部分更新数据（不含shape）
 * @returns {Promise}
 */
export function partialUpdateManagementOtherarea(id, otherareaData) {
  // 检查是否包含shape字段，如果包含则拒绝
  if ('shape' in otherareaData) {
    return Promise.reject(new Error('Shape attribute cannot be updated in management module'))
  }

  return request(`api/management/otherarea/${id}/`, {
    method: 'PATCH',
    body: otherareaData
  })
}

/**
 * 删除指定其他区域
 * @param {number} id - 其他区域ID
 * @returns {Promise}
 */
export function deleteManagementOtherarea(id) {
  return request(`api/management/otherarea/${id}/`, {
    method: 'DELETE'
  })
}

// ---------- 活动（Event）管理 ----------

/**
 * 获取所有活动列表
 * @returns {Promise}
 */
export function listManagementEvents() {
  return request('api/management/event/', {
    method: 'GET'
  })
}

/**
 * 获取指定活动详情
 * @param {number} id - 活动ID
 * @returns {Promise}
 */
export function getManagementEvent(id) {
  return request(`api/management/event/${id}/`, {
    method: 'GET'
  })
}

/**
 * 创建新的活动
 * @param {Object} eventData - 活动数据
 * @returns {Promise}
 */
export function createManagementEvent(eventData) {
  return request('api/management/event/', {
    method: 'POST',
    body: eventData
  })
}

/**
 * 完整更新活动
 * @param {number} id - 活动ID
 * @param {Object} eventData - 完整更新数据
 * @returns {Promise}
 */
export function updateManagementEvent(id, eventData) {
  return request(`api/management/event/${id}/`, {
    method: 'PUT',
    body: eventData
  })
}

/**
 * 部分更新活动
 * @param {number} id - 活动ID
 * @param {Object} eventData - 部分更新数据
 * @returns {Promise}
 */
export function partialUpdateManagementEvent(id, eventData) {
  return request(`api/management/event/${id}/`, {
    method: 'PATCH',
    body: eventData
  })
}

/**
 * 删除指定活动
 * @param {number} id - 活动ID
 * @returns {Promise}
 */
export function deleteManagementEvent(id) {
  return request(`api/management/event/${id}/`, {
    method: 'DELETE'
  })
}

// ---------- 店铺区域（Storearea）管理 ----------

/**
 * 获取所有店铺区域列表
 * @returns {Promise}
 */
export function listManagementStoreareas() {
  return request('api/management/storearea/', {
    method: 'GET'
  })
}

/**
 * 获取指定店铺区域详情
 * @param {number} id - 店铺区域ID
 * @returns {Promise}
 */
export function getManagementStorearea(id) {
  return request(`api/management/storearea/${id}/`, {
    method: 'GET'
  })
}

/**
 * 创建新的店铺区域（自动移除shape字段）
 * @param {Object} storeareaData - 店铺区域数据（不含shape）
 * @returns {Promise}
 */
export function createManagementStorearea(storeareaData) {
  // 确保不包含shape字段
  const data = { ...storeareaData }
  if ('shape' in data) {
    console.warn('Warning: shape字段将在management.create中被自动移除')
    delete data.shape
  }

  return request('api/management/storearea/', {
    method: 'POST',
    body: data
  })
}

/**
 * 完整更新店铺区域（不允许更新shape）
 * @param {number} id - 店铺区域ID
 * @param {Object} storeareaData - 完整更新数据（不含shape）
 * @returns {Promise}
 */
export function updateManagementStorearea(id, storeareaData) {
  // 检查是否包含shape字段，如果包含则拒绝
  if ('shape' in storeareaData) {
    return Promise.reject(new Error('Shape attribute cannot be updated in management module'))
  }

  return request(`api/management/storearea/${id}/`, {
    method: 'PUT',
    body: storeareaData
  })
}

/**
 * 部分更新店铺区域（不允许更新shape）
 * @param {number} id - 店铺区域ID
 * @param {Object} storeareaData - 部分更新数据（不含shape）
 * @returns {Promise}
 */
export function partialUpdateManagementStorearea(id, storeareaData) {
  // 检查是否包含shape字段，如果包含则拒绝
  if ('shape' in storeareaData) {
    return Promise.reject(new Error('Shape attribute cannot be updated in management module'))
  }

  return request(`api/management/storearea/${id}/`, {
    method: 'PATCH',
    body: storeareaData
  })
}

/**
 * 删除指定店铺区域
 * @param {number} id - 店铺区域ID
 * @returns {Promise}
 */
export function deleteManagementStorearea(id) {
  return request(`api/management/storearea/${id}/`, {
    method: 'DELETE'
  })
}

// ---------- 设施（Facility）管理 ----------

/**
 * 获取所有设施列表
 * @returns {Promise}
 */
export function listManagementFacilities() {
  return request('api/management/facility/', {
    method: 'GET'
  })
}

/**
 * 获取指定设施详情
 * @param {number} id - 设施ID
 * @returns {Promise}
 */
export function getManagementFacility(id) {
  return request(`api/management/facility/${id}/`, {
    method: 'GET'
  })
}

/**
 * 创建新的设施（自动移除shape字段）
 * @param {Object} facilityData - 设施数据（不含shape）
 * @returns {Promise}
 */
export function createManagementFacility(facilityData) {
  // 确保不包含shape字段
  const data = { ...facilityData }
  if ('shape' in data) {
    console.warn('Warning: shape字段将在management.create中被自动移除')
    delete data.shape
  }

  return request('api/management/facility/', {
    method: 'POST',
    body: data
  })
}

/**
 * 完整更新设施（不允许更新shape）
 * @param {number} id - 设施ID
 * @param {Object} facilityData - 完整更新数据（不含shape）
 * @returns {Promise}
 */
export function updateManagementFacility(id, facilityData) {
  // 检查是否包含shape字段，如果包含则拒绝
  if ('shape' in facilityData) {
    return Promise.reject(new Error('Shape attribute cannot be updated in management module'))
  }

  return request(`api/management/facility/${id}/`, {
    method: 'PUT',
    body: facilityData
  })
}

/**
 * 部分更新设施（不允许更新shape）
 * @param {number} id - 设施ID
 * @param {Object} facilityData - 部分更新数据（不含shape）
 * @returns {Promise}
 */
export function partialUpdateManagementFacility(id, facilityData) {
  // 检查是否包含shape字段，如果包含则拒绝
  if ('shape' in facilityData) {
    return Promise.reject(new Error('Shape attribute cannot be updated in management module'))
  }

  return request(`api/management/facility/${id}/`, {
    method: 'PATCH',
    body: facilityData
  })
}

/**
 * 删除指定设施
 * @param {number} id - 设施ID
 * @returns {Promise}
 */
export function deleteManagementFacility(id) {
  return request(`api/management/facility/${id}/`, {
    method: 'DELETE'
  })
}

/**
 * 批量更新区域状态（启用/停用）
 * @param {Array<number>} ids - 区域ID数组
 * @param {boolean} isActive - 新的状态
 * @returns {Promise}
 */
export function batchUpdateAreaStatus(ids, isActive) {
  // 这里实现批量操作，可以调用相应的批量更新接口
  // 如果没有批量接口，可以依次调用单个更新接口
  const promises = ids.map(id =>
    partialUpdateManagementStorearea(id, { is_active: isActive })
      .catch(() => partialUpdateManagementEventarea(id, { is_active: isActive }))
      .catch(() => partialUpdateManagementOtherarea(id, { is_active: isActive }))
      .catch(() => partialUpdateManagementFacility(id, { is_active: isActive }))
  )

  return Promise.allSettled(promises)
}

/**
 * 根据区域类型和ID获取区域详情（通用方法）
 * @param {string} type - 区域类型：'storearea', 'eventarea', 'otherarea', 'event', 'facility'
 * @param {number} id - 区域ID
 * @returns {Promise}
 */
export function getAreaByTypeAndId(type, id) {
  const typeMap = {
    storearea: getManagementStorearea,
    eventarea: getManagementEventarea,
    otherarea: getManagementOtherarea,
    event: getManagementEvent,
    facility: getManagementFacility
  }

  const handler = typeMap[type]
  if (!handler) {
    return Promise.reject(new Error(`Unsupported area type: ${type}`))
  }

  return handler(id)
}

/**
 * 根据区域类型和ID更新区域（通用方法）
 * @param {string} type - 区域类型：'storearea', 'eventarea', 'otherarea', 'event', 'facility'
 * @param {number} id - 区域ID
 * @param {Object} data - 更新数据
 * @param {boolean} partial - 是否为部分更新，默认为true
 * @returns {Promise}
 */
export function updateAreaByTypeAndId(type, id, data, partial = true) {
  const typeMap = {
    storearea: partial ? partialUpdateManagementStorearea : updateManagementStorearea,
    eventarea: partial ? partialUpdateManagementEventarea : updateManagementEventarea,
    otherarea: partial ? partialUpdateManagementOtherarea : updateManagementOtherarea,
    event: partial ? partialUpdateManagementEvent : updateManagementEvent,
    facility: partial ? partialUpdateManagementFacility : updateManagementFacility
  }

  const handler = typeMap[type]
  if (!handler) {
    return Promise.reject(new Error(`Unsupported area type: ${type}`))
  }

  return handler(id, data)
}

// ---------- 默认导出 ----------

export default {
  // 管理员认证
  adminRegister,
  adminLogin,
  adminLogout,
  getAdminProfile,
  updateAdminProfile,

  // 活动区域管理
  listManagementEventareas,
  getManagementEventarea,
  createManagementEventarea,
  updateManagementEventarea,
  partialUpdateManagementEventarea,
  deleteManagementEventarea,

  // 其他区域管理
  listManagementOtherareas,
  getManagementOtherarea,
  createManagementOtherarea,
  updateManagementOtherarea,
  partialUpdateManagementOtherarea,
  deleteManagementOtherarea,

  // 活动管理
  listManagementEvents,
  getManagementEvent,
  createManagementEvent,
  updateManagementEvent,
  partialUpdateManagementEvent,
  deleteManagementEvent,

  // 店铺区域管理
  listManagementStoreareas,
  getManagementStorearea,
  createManagementStorearea,
  updateManagementStorearea,
  partialUpdateManagementStorearea,
  deleteManagementStorearea,

  // 设施管理
  listManagementFacilities,
  getManagementFacility,
  createManagementFacility,
  updateManagementFacility,
  partialUpdateManagementFacility,
  deleteManagementFacility,

  // 批量操作和辅助函数
  batchUpdateAreaStatus,
  getAreaByTypeAndId,
  updateAreaByTypeAndId
}
