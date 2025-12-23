const formatTime = date => {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours()
  const minute = date.getMinutes()
  const second = date.getSeconds()

  return `${[year, month, day].map(formatNumber).join('/')} ${[hour, minute, second].map(formatNumber).join(':')}`
}

const formatNumber = n => {
  n = n.toString()
  return n[1] ? n : `0${n}`
}

module.exports = {
  formatTime
}

// 后端 API 基础地址（开发时使用 localhost:8081，生产可替换）
const baseUrl = 'http://localhost:8081/api'

function apiRequest(path, method = 'GET', data = {}, options = {}) {
  const url = baseUrl + path
  // 是否随请求携带凭证（Cookie）
  const withCredentials = !!options.withCredentials

  const makeRequest = (reqUrl) => new Promise((resolve, reject) => {
    wx.request({
      url: reqUrl,
      method,
      data,
      header: Object.assign({'content-type': 'application/json'}, options.header || {}),
      withCredentials,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          console.error('API request non-2xx', reqUrl, res.statusCode, res.data)
          reject(res)
        }
      },
      fail(err) {
        console.error('API request failed', reqUrl, err)
        reject(err)
      }
    })
  })

  // 首先尝试配置的 baseUrl
  return makeRequest(url).catch(err => {
    // 如果 baseUrl 包含 '/api'，尝试回退到不带 '/api' 的 base URL（兼容后端不同前缀）
    if (baseUrl.includes('/api')) {
      const altBase = baseUrl.replace(/\/api\/?$/, '')
      const altUrl = altBase + path
      console.warn('Retrying with alternative base URL:', altUrl)
      return makeRequest(altUrl)
    }
    return Promise.reject(err)
  })
}

module.exports = Object.assign({}, module.exports, { baseUrl, apiRequest })
