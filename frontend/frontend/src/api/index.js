// API 公共配置与 helper
const BACKEND_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8081'

function buildUrl(path) {
  return `${BACKEND_BASE.replace(/\/+$/, '')}/${path.replace(/^\/+/, '')}`
}

async function request(path, options = {}) {
  const url = buildUrl(path)
  const opts = Object.assign({
    headers: {
      'Content-Type': 'application/json'
    }
  }, options)

  if (opts.body && typeof opts.body === 'object') {
    opts.body = JSON.stringify(opts.body)
  }

  const res = await fetch(url, opts)
  const contentType = res.headers.get('content-type') || ''
  let data = null
  if (contentType.includes('application/json')) {
    data = await res.json()
  } else {
    data = await res.text()
  }

  if (!res.ok) {
    const err = new Error(data?.detail || res.statusText || 'API error')
    err.status = res.status
    err.data = data
    throw err
  }

  return data
}

export { BACKEND_BASE, buildUrl, request }
