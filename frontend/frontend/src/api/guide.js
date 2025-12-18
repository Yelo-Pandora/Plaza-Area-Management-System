import { request } from './index'

/**
 * 导览相关 API 封装
 * 后端接口：POST /api/guide/route/
 */

// 计算从起点到终点的路径
// payload 示例：
// { map_id: 1, start: { x: 10, y: 20 }, end: { x: 50, y: 60 } }
export function planRoute(payload) {
  return request('api/guide/route/', {
    method: 'POST',
    body: payload
  })
}

