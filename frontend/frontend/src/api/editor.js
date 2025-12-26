import { request } from './index'

/**
 * Editor 模块：负责地图上的几何图形编辑与部分关联关系管理
 * 前缀：/api/editor/
 *
 * 约定：
 * - 在 editor 模块中，只修改 / 创建几何字段（shape），属性信息交由 management 模块处理
 * - geometry 统一使用 GeoJSON 对象（前端负责与绘图库对接）
 */

// ---------- Storearea（店铺区域）几何 ----------

export function listEditorStoreareas() {
  return request('api/editor/storearea/', { method: 'GET' })
}

export function getEditorStorearea(id) {
  return request(`api/editor/storearea/${id}/`, { method: 'GET' })
}

// 只传 shape 字段 + map_id：后端期望 shape 为字符串（WKT 或 GeoJSON 字符串）
export function createEditorStorearea(shapeGeojson, map_id) {
  return request('api/editor/storearea/', {
    method: 'POST',
    body: {
      shape: typeof shapeGeojson === 'string' ? shapeGeojson : JSON.stringify(shapeGeojson),
      map_id
    }
  })
}

export function updateEditorStoreareaShape(id, shapeGeojson) {
  return request(`api/editor/storearea/${id}/`, {
    method: 'PATCH',
    body: { shape: typeof shapeGeojson === 'string' ? shapeGeojson : JSON.stringify(shapeGeojson) }
  })
}

export function deleteEditorStorearea(id) {
  return request(`api/editor/storearea/${id}/`, { method: 'DELETE' })
}

// 获取某个店铺区域关联的所有活动 ID
export function getStoreareaEventsForEditor(id) {
  return request(`api/editor/storearea/${id}/events/`, { method: 'GET' })
}

// ---------- Event（活动）只读 + 关联关系 ----------

export function listEditorEvents() {
  return request('api/editor/event/', { method: 'GET' })
}

export function getEditorEvent(id) {
  return request(`api/editor/event/${id}/`, { method: 'GET' })
}

// 获取活动关联的所有区域 ID
export function getEventAreasForEditor(id) {
  return request(`api/editor/event/${id}/areas/`, { method: 'GET' })
}

// 管理活动与店铺区域的关联（POST 创建 / DELETE 删除）
export function addStoreareaToEvent(eventId, storeareaId) {
  return request(`api/editor/event/${eventId}/storeareas/`, {
    method: 'POST',
    body: { storearea_id: storeareaId }
  })
}

export function removeStoreareaFromEvent(eventId, storeareaId) {
  return request(`api/editor/event/${eventId}/storeareas/`, {
    method: 'DELETE',
    body: { storearea_id: storeareaId }
  })
}

// ---------- Eventarea（活动区域）几何 ----------

export function listEditorEventareas() {
  return request('api/editor/eventarea/', { method: 'GET' })
}

export function getEditorEventarea(id) {
  return request(`api/editor/eventarea/${id}/`, { method: 'GET' })
}

export function createEditorEventarea(shapeGeojson, map_id) {
  return request('api/editor/eventarea/', {
    method: 'POST',
    body: {
      shape: typeof shapeGeojson === 'string' ? shapeGeojson : JSON.stringify(shapeGeojson),
      map_id
    }
  })
}

export function updateEditorEventareaShape(id, shapeGeojson) {
  return request(`api/editor/eventarea/${id}/`, {
    method: 'PATCH',
    body: { shape: typeof shapeGeojson === 'string' ? shapeGeojson : JSON.stringify(shapeGeojson) }
  })
}

export function deleteEditorEventarea(id) {
  return request(`api/editor/eventarea/${id}/`, { method: 'DELETE' })
}

// ---------- Otherarea（其他区域）几何 + 与 Eventarea 关联 ----------

export function listEditorOtherareas() {
  return request('api/editor/otherarea/', { method: 'GET' })
}

export function getEditorOtherarea(id) {
  return request(`api/editor/otherarea/${id}/`, { method: 'GET' })
}

export function createEditorOtherarea(shapeGeojson, map_id, type = 0) {
  return request('api/editor/otherarea/', {
    method: 'POST',
    body: {
      shape: typeof shapeGeojson === 'string' ? shapeGeojson : JSON.stringify(shapeGeojson),
      map_id,
      type
    }
  })
}

export function updateEditorOtherareaShape(id, shapeGeojson) {
  return request(`api/editor/otherarea/${id}/`, {
    method: 'PATCH',
    body: { shape: typeof shapeGeojson === 'string' ? shapeGeojson : JSON.stringify(shapeGeojson) }
  })
}

export function deleteEditorOtherarea(id) {
  return request(`api/editor/otherarea/${id}/`, { method: 'DELETE' })
}

// 管理活动与活动区域的关联关系
export function addEventareaToEvent(eventId, eventareaId) {
  return request(`api/editor/otherarea/${eventId}/eventareas/`, {
    method: 'POST',
    body: { eventarea_id: eventareaId }
  })
}

export function removeEventareaFromEvent(eventId, eventareaId) {
  return request(`api/editor/otherarea/${eventId}/eventareas/`, {
    method: 'DELETE',
    body: { eventarea_id: eventareaId }
  })
}

export function updateEditorFacilityLocation(id, locationGeojson) {
  return request(`api/editor/facility/${id}/`, {
    method: 'PATCH',
    body: {
      // 后端 Facility 模型使用的是 location 字段
      location: typeof locationGeojson === 'string' ? locationGeojson : JSON.stringify(locationGeojson)
    }
  })
}

export function deleteEditorFacility(id) {
  return request(`api/editor/facility/${id}/`, { method: 'DELETE' })
}
