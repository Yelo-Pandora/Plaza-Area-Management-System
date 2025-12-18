import { request } from './index'

/**
 * 地图相关 API 封装
 * 后端接口见：/api/maps/ 与 /api/maps/validate/
 */

// 获取所有地图（楼层）列表
export function listMaps() {
  return request('api/maps/', { method: 'GET' })
}

// 获取单个地图详情（包含底图 geometry 和各类区域要素）
export function getMapById(id) {
  return request(`api/maps/${id}/`, { method: 'GET' })
}

// 校验某个几何图形是否与现有地图/区域冲突
// payload 示例：
// { geometry: <GeoJSON对象或字符串>, map_id: 1, type: 1, exclude_id: 10 }
export function validateGeometry(payload) {
  return request('api/maps/validate/', {
    method: 'POST',
    body: payload
  })
}

