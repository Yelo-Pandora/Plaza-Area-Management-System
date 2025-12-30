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
const baseUrl = 'http://http://yauycf.top/:8081/api'

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
      timeout:20000, // 显示指定单次请求的超时 20s 路径规划可能需要较长时间
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

  // 始终使用配置的 baseUrl（避免回退到不带 /api 导致接口命中错误前缀）
  return makeRequest(url)
}

module.exports = Object.assign({}, module.exports, { baseUrl, apiRequest })
