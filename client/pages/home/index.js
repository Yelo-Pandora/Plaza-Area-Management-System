// pages/home/index.js
const util = require('../../utils/util')

// ===== 类型映射（用于首页地图详情弹窗显示） =====
// 设施类型（示例：1 代表消防栓）
const FACILITY_TYPE_MAP = {
  0: '电动扶梯',
  1: '灭火器',
  2: '安全出口',
  3: '服务台',
  4: '其他',
}

// 设施图标映射（canvas drawImage 需要位图资源；已将 svg 转为同名 png）
const FACILITY_ICON_MAP = {
  0: '/images/facility/escalator.png',
  1: '/images/facility/fire_extinguisher.png',
  2: '/images/facility/exit.png',
  3: '/images/facility/info.png',
  4: '/images/facility/other.png',
}

// 设施图标底盘颜色（不同类型使用不同底色，提升白色图标在白底地图上的可读性）
const FACILITY_ICON_BASE_COLOR = {
  0: 'rgba(24,144,255,0.95)',   // 电梯/扶梯：蓝
  1: 'rgba(220,38,38,0.95)',    // 灭火器：红
  2: 'rgba(34,197,94,0.95)',    // 安全出口：绿
  3: 'rgba(245,158,11,0.95)',   // 服务台：黄
  4: 'rgba(255,120,40,0.95)',   // 其他：橙
}

// 活动区域“类型”映射（示例：1——促销活动）
// 注意：这里映射的是“活动类型码”，不是 eventarea/storearea 这种区域大类。
const EVENT_AREA_TYPE_MAP = {
  0: '其他活动',
  1: '促销活动',
  2: '展览活动',
  3: '表演活动',
}

// 其他区域“类型”映射（按你的后端类型码补全）
const OTHER_AREA_TYPE_MAP = {
  0: '公共区域',
  1: '卫生间',
  2: '电梯间',
  3: '其他',
}

// 区域大类（eventarea/storearea/otherarea...）
const AREA_TYPE_MAP = {
  eventarea: '活动区域',
  storearea: '商铺区域',
  otherarea: '其他区域',
  publicarea: '公共区域'
}

Page({
  data: {
    recommended: [],
    maps: [],
    selectedMapIndex: 0,
    // canvas transforms
    scale: 1,
    offsetX: 0,
    offsetY: 0,
    showRegionModal: false,
    activeRegion: null
    ,showZoomPercent: false,
    zoomPercent: 100
  },

  noop() {},

  onPageScroll(e) {
    const scrollTop = (e && typeof e.scrollTop === 'number') ? e.scrollTop : 0
    this._pageScrollTop = scrollTop

    // 弹窗打开时锁定页面滚动：避免滚轮/触摸导致背景滚动并“盖住”弹窗
    if (this.data.showRegionModal) {
      if (this._lockScrollTop === undefined || this._lockScrollTop === null) {
        this._lockScrollTop = scrollTop
        return
      }
      if (this._restoringScroll) return
      if (Math.abs(scrollTop - this._lockScrollTop) > 2) {
        this._restoringScroll = true
        wx.pageScrollTo({
          scrollTop: this._lockScrollTop,
          duration: 0,
          complete: () => { this._restoringScroll = false }
        })
      }
    }
  },

  onLoad(options) {
    this.fetchRecommendations()
    this.fetchMaps()
  },

  fetchRecommendations() {
    // 调用后端活动列表接口，取得推荐活动（不传 type 时后端按分类返回）
    util.apiRequest('/search/event/list/').then(res => {
      // 如果返回带 'events' 字段，则取它；否则把所有分类合并为一维数组展示
      let arr = []
      if (res && res.events) {
        arr = res.events
      } else if (res && typeof res === 'object') {
        Object.keys(res).forEach(k => {
          const list = res[k] || []
          list.forEach(it => arr.push(it))
        })
      }

      // 固定挑选 6 个作为首页推荐，并规范化字段用于展示
      const pick = this._pickRandomSubset(arr, 6).map(it => this._normalizeEventForHome(it))
      this.setData({ recommended: pick })
    }).catch(err => {
      console.error('获取推荐活动失败', err)
    })
  },

  _pickRandomSubset(arr, n) {
    if (!Array.isArray(arr) || arr.length === 0) return []
    const copy = arr.slice()
    // Fisher-Yates 随机打乱
    for (let i = copy.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      const t = copy[i]; copy[i] = copy[j]; copy[j] = t
    }
    return copy.slice(0, Math.min(n, copy.length))
  },

  // ---------- Event normalization for home list (reuse logic from activities) ----------
  _isOngoing(endVal) {
    if (!endVal) return false
    try {
      let d
      if (typeof endVal === 'string') {
        const s = endVal.trim()
        if (/^\d{4}-\d{2}-\d{2} /.test(s)) {
          d = new Date(s.replace(' ', 'T'))
        } else {
          d = new Date(s)
        }
      } else {
        d = new Date(endVal)
      }
      if (isNaN(d.getTime())) return false
      return Date.now() <= d.getTime()
    } catch (e) {
      return false
    }
  },

  _formatDateStr(s) {
    if (!s) return ''
    try {
      if (typeof s === 'string' && s.length >= 16 && s[4] === '-') return s.substr(0,16)
      const d = new Date(s)
      if (!isNaN(d.getTime())) {
        const y = d.getFullYear()
        const m = (d.getMonth()+1).toString().padStart(2,'0')
        const day = d.getDate().toString().padStart(2,'0')
        const hh = d.getHours().toString().padStart(2,'0')
        const mm = d.getMinutes().toString().padStart(2,'0')
        return `${y}-${m}-${day} ${hh}:${mm}`
      }
    } catch (e) {}
    return s
  },

  _normalizeEventForHome(raw) {
    if (!raw || typeof raw !== 'object') return raw
    const ev = Object.assign({}, raw)
    ev.id = ev.id || ev.event_id || ev.pk || ev.uuid || ev._id
    ev.name = ev.name || ev.event_name || ev.title || ev.eventTitle || '活动'
    ev.description = ev.description || ev.desc || ev.detail || ev.description_text || ev.summary || ''
    ev.type_name = ev.type_name || ev.type || ev.category || ev.typeName || ''
    ev.start = ev.start || ev.start_date || ev.start_time || ev.date || ev.begin || ev.startDate || ev.begin_time
    ev.end = ev.end || ev.end_date || ev.end_time || ev.finish || ev.endDate || ev.finish_time
    ev._raw_end = ev.end
    ev.is_ongoing = this._isOngoing(ev._raw_end)
    try { ev.start = this._formatDateStr(ev.start) } catch(e){}
    try { ev.end = this._formatDateStr(ev.end) } catch(e){}
    // image field compatibility
    ev.image_url = ev.image_url || ev.image || ev.imageUrl || ev.img || ev.thumbnail || ''
    return ev
  },

  openFullMap() {
    // 打开系统地图（演示），可改为跳转至地图详情页
    wx.openLocation({
      latitude: 22.6,
      longitude: 114.0,
      scale: 18,
      name: '广场'
    })
  },

  openActivity(e) {
    const id = e.currentTarget.dataset.id
    if (!id) return
    // 暂跳转到活动页（可实现活动详情页）
    wx.navigateTo({ url: `/pages/activities/index?event_id=${id}` })
  },

  // ========== Map / Canvas logic ==========
  fetchMaps() {
    util.apiRequest('/maps/').then(res => {
      // res expected to be array of maps
      const maps = (res || []).map(m => ({ id: m.id, label: `${m.building_name || ''} 楼层 ${m.floor_number}`, raw: m }))
      this.setData({ maps })
      if (maps.length) this.loadMapDetail(0)
    }).catch(err => console.error('加载地图列表失败', err))
  },

  onMapChange(e) {
    const idx = parseInt(e.detail.value, 10) || 0
    this.setData({ selectedMapIndex: idx, scale: 1, offsetX: 0, offsetY: 0, activeRegion: null })
    this.loadMapDetail(idx)
  },

  loadMapDetail(index) {
    const map = this.data.maps[index]
    if (!map) return
    util.apiRequest(`/maps/${map.id}/`).then(res => {
      // replace raw with detail
      const maps = this.data.maps.slice()
      maps[index].raw = res
      this.setData({ maps })
      // draw
      setTimeout(() => this.drawMap(), 50)
      // fetch facilities for this map/floor
      //this.fetchFacilitiesForMap(map.id)
    }).catch(err => console.error('加载地图详情失败', err))
  },

  // fetch facilities for a given map id from backend
  fetchFacilitiesForMap(mapId) {
    if (!mapId) return
    util.apiRequest(`/maps/${mapId}/facilities/`).then(res => {
      // expect array or {results: []}
      const list = Array.isArray(res) ? res : (res && res.results) ? res.results : []
      // attach to corresponding map.raw
      const maps = this.data.maps.slice()
      const idx = maps.findIndex(m => m.id === mapId)
      if (idx >= 0) {
        maps[idx].raw = Object.assign({}, maps[idx].raw || {}, { facilities: list })
        this.setData({ maps }, () => this.drawMap())
      }
    }).catch(err => {
      console.warn('加载设施数据失败', err)
    })
  },

  drawMap() {
    const idx = this.data.selectedMapIndex
    const map = this.data.maps[idx]
    if (!map || !map.raw) return

    const detail = map.raw.detail_geojson
    const ctx = wx.createCanvasContext('mapCanvas', this)
    // canvas size: get system info to compute pixel ratio
    const query = wx.createSelectorQuery().in(this)
    query.select('.map-canvas').boundingClientRect(rect => {
      // cache rect for touch handlers
      this._canvasRect = rect
      const w = rect.width, h = rect.height
      // clear
      ctx.clearRect(0, 0, w, h)

      if (!detail) {
        ctx.setFillStyle('#f5f5f5')
        ctx.fillRect(0,0,w,h)
        ctx.draw()
        return
      }

      // collect polygons from detail (GeoJSON)
      const polygons = []
      if (detail.type === 'GeometryCollection' && Array.isArray(detail.geometries)) {
        detail.geometries.forEach(g => {
          if (g.type === 'Polygon') polygons.push(g.coordinates)
          if (g.type === 'MultiPolygon') g.coordinates.forEach(c => polygons.push(c))
        })
      } else if (detail.type === 'Polygon') polygons.push(detail.coordinates)

      // compute bbox
      let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
      polygons.forEach(poly => {
        poly.forEach(ring => ring.forEach(pt => {
          const x = pt[0], y = pt[1]
          if (x < minX) minX = x
          if (y < minY) minY = y
          if (x > maxX) maxX = x
          if (y > maxY) maxY = y
        }))
      })
      if (!isFinite(minX)) {
        ctx.draw()
        return
      }

      const mapW = maxX - minX || 1
      const mapH = maxY - minY || 1
      // compute scale to fit
      const baseScale = Math.min(w / mapW, h / mapH)
      const s = baseScale * this.data.scale

      // helper to convert geo (x,y) to canvas
      const toCanvas = (x,y) => {
        // translate so minX maps to 0, minY maps to 0, then apply scale, then center
        const cx = (x - minX) * s + this.data.offsetX + (w - mapW * s)/2
        const cy = (y - minY) * s + this.data.offsetY + (h - mapH * s)/2
        return [cx, cy]
      }

      // draw base shell (first polygon as outer)
      ctx.setStrokeStyle('#333')
      ctx.setLineWidth(1)
      ctx.setFillStyle('#fff')
      polygons.forEach((poly, pi) => {
        // poly: array of rings; first is outer
        poly.forEach((ring, ri) => {
          ring.forEach((pt, i) => {
            const [cx, cy] = toCanvas(pt[0], pt[1])
            if (i === 0) ctx.moveTo(cx, cy)
            else ctx.lineTo(cx, cy)
          })
        })
        ctx.closePath()
        ctx.fill()
        ctx.stroke()
      })

      // draw regions (stores / other / events)
      const regions = []
      const pushGeo = (list, color, kind) => {
        (list || []).forEach(it => {
          if (!it.geometry) return
          try { const g = it.geometry; if (g.type === 'Polygon') regions.push({coords: g.coordinates, meta: it, color})
            else if (g.type === 'MultiPolygon') g.coordinates.forEach(c => regions.push({coords: c, meta: it, color}))
          } catch(e){}
        })
      }
      // 给不同来源的区域打上 kind，便于点击后正确分类（避免活动区域被当成其他区域）
      const pushRegion = (list, color, kind) => {
        (list || []).forEach(it => {
          if (!it.geometry) return
          try {
            const g = it.geometry
            if (g.type === 'Polygon') regions.push({ coords: g.coordinates, meta: it, color, kind })
            else if (g.type === 'MultiPolygon') g.coordinates.forEach(c => regions.push({ coords: c, meta: it, color, kind }))
          } catch (e) {}
        })
      }
      pushRegion(map.raw.stores, 'rgba(0,120,212,0.3)', 'storearea')
      pushRegion(map.raw.other_areas, 'rgba(120,200,80,0.3)', 'otherarea')
      pushRegion(map.raw.events, 'rgba(220,80,80,0.3)', 'eventarea')

      const showLabels = (this.data.scale || 1) >= 2.4
      const truncate = (text, maxChars) => {
        if (!text) return ''
        const s = String(text)
        if (s.length <= maxChars) return s
        return s.slice(0, Math.max(0, maxChars - 1)) + '…'
      }
      const drawLabel = (x, y, text, fontSize) => {
        if (!text) return
        const maxChars = 10
        const t = truncate(text, maxChars)
        ctx.setFontSize(fontSize)
        ctx.setTextAlign('center')
        ctx.setTextBaseline('middle')
        // 白色描边 + 深色填充：无外框但清晰
        ctx.setStrokeStyle('rgba(255,255,255,0.95)')
        ctx.setLineWidth(3)
        ctx.strokeText(t, x, y)
        ctx.setFillStyle('#111')
        ctx.fillText(t, x, y)
      }
      const centroidOfRing = (ring) => {
        if (!Array.isArray(ring) || ring.length < 3) return null
        // polygon centroid (area-weighted); fallback to average if degenerate
        let area = 0
        let cxSum = 0
        let cySum = 0
        for (let i = 0; i < ring.length - 1; i++) {
          const x0 = ring[i][0], y0 = ring[i][1]
          const x1 = ring[i + 1][0], y1 = ring[i + 1][1]
          const a = x0 * y1 - x1 * y0
          area += a
          cxSum += (x0 + x1) * a
          cySum += (y0 + y1) * a
        }
        if (Math.abs(area) < 1e-9) {
          let sx = 0, sy = 0
          ring.forEach(p => { sx += p[0]; sy += p[1] })
          return [sx / ring.length, sy / ring.length]
        }
        area *= 0.5
        return [cxSum / (6 * area), cySum / (6 * area)]
      }

      regions.forEach(r => {
        ctx.setFillStyle(r.color)
        ctx.beginPath()
        r.coords.forEach(ring => ring.forEach((pt, i) => {
          const [cx, cy] = toCanvas(pt[0], pt[1])
          if (i===0) ctx.moveTo(cx, cy)
          else ctx.lineTo(cx, cy)
        }))
        ctx.closePath()
        ctx.fill()
      })

      // labels on regions when zoomed in
      if (showLabels) {
        regions.forEach(r => {
          try {
            const ring = r.coords && r.coords[0]
            const c = centroidOfRing(ring)
            if (!c) return
            const [lx, ly] = toCanvas(c[0], c[1])

            const metaWithKind = (r && r.meta && typeof r.meta === 'object')
              ? Object.assign({}, r.meta, { __kind: r.kind })
              : r.meta
            const norm = this._normalizeRegionForModal(metaWithKind)
            let label = ''
            if (r.kind === 'storearea') {
              label = (norm && (norm.store_name || norm.name)) || (r.meta && (r.meta.store_name || r.meta.name || r.meta.title))
            } else {
              label = (norm && norm.type_display) || (r.kind === 'eventarea' ? '活动区域' : '其他区域')
            }
            drawLabel(lx, ly, label, 12)
          } catch (e) {}
        })
      }

      // draw facility markers (points)
      const facilities = (map.raw.facilities || []).filter(f => f.geometry && (f.geometry.type === 'Point' || f.geometry.type === 'MultiPoint'))
      ctx.setFillStyle('rgba(255,120,40,0.95)')
      facilities.forEach(f => {
        try {
          const coords = f.geometry.type === 'Point' ? f.geometry.coordinates : (f.geometry.coordinates && f.geometry.coordinates[0])
          if (!coords) return
          const [fx, fy] = coords
          const [cx, cy] = toCanvas(fx, fy)
            const norm = this._normalizeRegionForModal(f)
            const code = (norm && (norm.type_code ?? norm.facility_type ?? norm.type))
            const num = Number(code)
            const hasNum = !Number.isNaN(num) && Number.isFinite(num)
            const key = hasNum ? num : String(code)
            const icon = FACILITY_ICON_MAP[key]
            const baseColor = FACILITY_ICON_BASE_COLOR[key] || 'rgba(24,144,255,0.95)'

            // icon size grows with zoom but clamps to keep readable (slightly smaller)
            const iconSize = Math.max(10, Math.min(22, Math.round(10 * (this.data.scale || 1))))
            if (icon) {
              // 白色图标在白底地图上不清晰：先画一个高对比底座再叠加图标
              if (typeof ctx.setShadow === 'function') {
                ctx.setShadow(0, 3, 8, 'rgba(0,0,0,0.22)')
              }
              ctx.setFillStyle(baseColor)
              ctx.beginPath()
              ctx.arc(cx, cy, (iconSize / 2) + 1, 0, Math.PI * 2)
              ctx.fill()
              if (typeof ctx.setShadow === 'function') {
                ctx.setShadow(0, 0, 0, 'rgba(0,0,0,0)')
              }
              ctx.drawImage(icon, cx - iconSize / 2, cy - iconSize / 2, iconSize, iconSize)
            } else {
              // fallback to dot marker
              ctx.setFillStyle('rgba(255,120,40,0.95)')
              const rMark = Math.max(2, Math.min(6, Math.round(2 * (baseScale * this.data.scale))))
              ctx.beginPath()
              ctx.arc(cx, cy, rMark, 0, Math.PI * 2)
              ctx.fill()
            }

          if (showLabels) {
            const norm = this._normalizeRegionForModal(f)
            const label = norm && norm.type_display
            // 将文字绘制在 marker 附近（居中）
            drawLabel(cx, cy - 18, label, 11)
          }
        } catch (e) {}
      })

      // save regions and facilities for hit-testing
      this._drawn = { polygons, regions, minX, minY, mapW, mapH, baseScale, canvasW: w, canvasH: h, facilities }
      ctx.draw()
    }).exec()
  },

  // touch handlers for pan
  onTouchStart(e) {
    const touches = e.touches || []
    if (touches.length >= 2) {
      // pinch start
      const r = this._canvasRect
      const p1 = touches[0]
      const p2 = touches[1]
      const x1 = p1.clientX - (r ? r.left : 0)
      const y1 = p1.clientY - (r ? r.top : 0)
      const x2 = p2.clientX - (r ? r.left : 0)
      const y2 = p2.clientY - (r ? r.top : 0)
      const distance = Math.hypot(x2 - x1, y2 - y1)
      const centerClient = { x: (x1 + x2) / 2, y: (y1 + y2) / 2 }
      // compute geo center using current transform
      const d = this._drawn
      if (d) {
        const s = d.baseScale * this.data.scale
        const centerPadX = (r.width - d.mapW * s) / 2
        const centerPadY = (r.height - d.mapH * s) / 2
        const geoX = (centerClient.x - this.data.offsetX - centerPadX) / s + d.minX
        const geoY = (centerClient.y - this.data.offsetY - centerPadY) / s + d.minY
        this._pinchStart = { distance, centerClient, baseScaleValue: this.data.scale, geoCenter: { x: geoX, y: geoY } }
      }
    } else if (touches.length === 1) {
      const t = touches[0]
      this._touchStart = { x: t.clientX, y: t.clientY, startOffsetX: this.data.offsetX, startOffsetY: this.data.offsetY }
    }
  },
  onTouchMove(e) {
    const touches = e.touches || []
    // pinch handling
    if (touches.length >= 2 && this._pinchStart && this._canvasRect && this._drawn) {
      const r = this._canvasRect
      const p1 = touches[0]
      const p2 = touches[1]
      const x1 = p1.clientX - r.left
      const y1 = p1.clientY - r.top
      const x2 = p2.clientX - r.left
      const y2 = p2.clientY - r.top
      const distance = Math.hypot(x2 - x1, y2 - y1)
      const scaleFactor = distance / this._pinchStart.distance
      let newScale = this._pinchStart.baseScaleValue * scaleFactor
      // clamp scale
      newScale = Math.max(0.2, Math.min(newScale, 6))

      // compute new offsets so geoCenter stays under same client center
      const d = this._drawn
      const sPrime = d.baseScale * newScale
      const centerClient = { x: (x1 + x2) / 2, y: (y1 + y2) / 2 }
      const centerPadX = (r.width - d.mapW * sPrime) / 2
      const centerPadY = (r.height - d.mapH * sPrime) / 2

      const geo = this._pinchStart.geoCenter
      const offsetX = centerClient.x - (geo.x - d.minX) * sPrime - centerPadX
      const offsetY = centerClient.y - (geo.y - d.minY) * sPrime - centerPadY

      this.setData({ scale: newScale, offsetX, offsetY }, () => {
        this.drawMap()
        this._showZoomPercent()
      })
      return
    }

    // single-touch pan
    const t = touches[0]
    if (!t || !this._touchStart) return
    const dx = t.clientX - this._touchStart.x
    const dy = t.clientY - this._touchStart.y
    this.setData({ offsetX: this._touchStart.startOffsetX + dx, offsetY: this._touchStart.startOffsetY + dy }, () => this.drawMap())
  },
  onTouchEnd(e) {
    // clear touch/pinch state
    this._touchStart = null
    this._pinchStart = null
  },

  // zoom buttons
  zoomIn() {
    const newScale = Math.min(this.data.scale * 1.2, 6)
    this.setData({ scale: newScale }, () => {
      this.drawMap()
      this._showZoomPercent()
    })
  },
  zoomOut() {
    const newScale = Math.max(this.data.scale / 1.2, 0.2)
    this.setData({ scale: newScale }, () => {
      this.drawMap()
      this._showZoomPercent()
    })
  },

  _showZoomPercent() {
    try { if (this._zoomTimer) clearTimeout(this._zoomTimer) } catch (e) {}
    const pct = Math.round((this.data.scale || 1) * 100)
    this.setData({ showZoomPercent: true, zoomPercent: pct })
    this._zoomTimer = setTimeout(() => {
      this.setData({ showZoomPercent: false })
      this._zoomTimer = null
    }, 800)
  },

  // tap to detect region
  onCanvasTap(e) {
    // compute client coords
    const clientX = (e.changedTouches && e.changedTouches[0] && e.changedTouches[0].clientX) || (e.touches && e.touches[0] && e.touches[0].clientX) || e.detail.x
    const clientY = (e.changedTouches && e.changedTouches[0] && e.changedTouches[0].clientY) || (e.touches && e.touches[0] && e.touches[0].clientY) || e.detail.y
    if (!this._drawn) return

    // get canvas position to convert client coords -> canvas local coords
    const query = wx.createSelectorQuery().in(this)
    query.select('.map-canvas').boundingClientRect(rect => {
      if (!rect) return
      const relX = clientX - rect.left
      const relY = clientY - rect.top

      const d = this._drawn
      const { minX, minY, baseScale, mapW, mapH } = d
      const s = baseScale * this.data.scale
      const gx = (relX - this.data.offsetX - (rect.width - mapW * s)/2)/s + minX
      const gy = (relY - this.data.offsetY - (rect.height - mapH * s)/2)/s + minY

      // check facility points first (prefer tapping marker)
      let hit = null
      if (d.facilities && d.facilities.length) {
        const sVal = d.baseScale * this.data.scale
        const padX = (rect.width - d.mapW * sVal)/2
        const padY = (rect.height - d.mapH * sVal)/2
        for (let i=0;i<d.facilities.length;i++){
          const f = d.facilities[i]
          try {
            const coords = f.geometry.type === 'Point' ? f.geometry.coordinates : (f.geometry.coordinates && f.geometry.coordinates[0])
            if (!coords) continue
            const fx = (coords[0] - d.minX) * sVal + this.data.offsetX + padX
            const fy = (coords[1] - d.minY) * sVal + this.data.offsetY + padY
            const dist = Math.hypot(relX - fx, relY - fy)
            if (dist <= 12) { hit = { meta: f, type: 'facility' }; break }
          } catch(e){}
        }
      }

      // then check polygon regions
      if (!hit) {
        hit = d.regions.find(r => {
          const ring = r.coords[0]
          return ring && this._pointInPoly([gx, gy], ring)
        })
      }

      if (hit) {
        // if facility marker, show meta; if polygon region, include its kind for correct classification
        let meta = hit.meta || (hit.type === 'facility' ? hit.meta : null)
        if (hit.kind && meta && typeof meta === 'object') {
          // 不直接污染原对象，浅拷贝并带上 __kind
          meta = Object.assign({}, meta, { __kind: hit.kind })
        }
        const norm = this._normalizeRegionForModal(meta)
        // 锁定当前滚动位置，避免弹窗打开后仍可滚动背景
        this._lockScrollTop = this._pageScrollTop || 0
        this.setData({ showRegionModal: true, activeRegion: norm })
        // 若规范化后缺少组织者/联系方式，尝试通过 search 模块的详情接口获取更详细的区域信息
        try {
          const areaId = (norm && norm._raw && (norm._raw.id || norm._raw.pk)) || (norm && (norm.id || norm.pk))
          // 设施弹窗只需展示类型：不要再发起详情请求，避免合并结果覆盖 is_facility 导致走回退分支
          if (areaId && !norm.is_facility && !norm.organizer_name && !norm.organizer_phone) {
            // 根据类型选择合适的 search 接口；活动区域不要回退到 otherarea，避免覆盖分类
            const tryPaths = []
            if (norm.is_event) {
              tryPaths.push(`/search/eventarea/${areaId}/`)
            } else if (norm.is_shop) {
              tryPaths.push(`/search/storearea/${areaId}/`)
            } else {
              tryPaths.push(`/search/otherarea/${areaId}/`)
            }

            const tryFetch = (i) => {
              if (i >= tryPaths.length) return Promise.reject(new Error('no search endpoint succeeded'))
              const p = tryPaths[i]
              return util.apiRequest(p).then(detail => ({ detail, path: p })).catch(err => tryFetch(i+1))
            }

            tryFetch(0).then(({ detail, path }) => {
              try {
                const more = this._normalizeRegionForModal(detail)
                // 合并时保留点击命中的分类信息，避免被返回数据覆盖导致弹窗分支错误
                const merged = Object.assign({}, norm, more)
                merged.is_facility = !!(norm.is_facility || more.is_facility)
                merged.is_shop = !!(norm.is_shop || more.is_shop)
                merged.is_event = !!(norm.is_event || more.is_event)
                merged.area_type = merged.area_type || norm.area_type || more.area_type
                const mergedRaw = Object.assign({}, (norm && norm._raw) ? norm._raw : {}, (more && more._raw) ? more._raw : {})
                if (norm && norm._raw && norm._raw.__kind && !mergedRaw.__kind) mergedRaw.__kind = norm._raw.__kind
                merged._raw = mergedRaw
                merged.type_display = this._getRegionTypeDisplay(merged)
                this.setData({ activeRegion: merged })
              } catch (e) { console.warn('normalize fetched area failed', e) }
            }).catch(err => {
              try { console.warn('fetch area detail via search endpoints failed', err) } catch(e){}
            })
          }
        } catch (e) { console.warn('area detail fetch prepare failed', e) }
      }
    }).exec()
  },

  // normalize various backend shapes into common fields used by modal
  _formatTypeCodeDisplay(code, map, unknownPrefix) {
    if (code === undefined || code === null || code === '') return ''
    const num = Number(code)
    const hasNum = !Number.isNaN(num) && Number.isFinite(num)
    const key = hasNum ? num : String(code)
    const label = map ? map[key] : undefined
    if (label) return label
    return unknownPrefix ? `${unknownPrefix}${hasNum ? num : String(code)}` : String(code)
  },

  _formatFacilityTypeDisplay(code) {
    if (code === undefined || code === null || code === '') return ''
    const num = Number(code)
    const hasNum = !Number.isNaN(num) && Number.isFinite(num)
    const key = hasNum ? num : String(code)
    const label = FACILITY_TYPE_MAP[key]
    if (label) return `${label}`
    return `未知设施：${hasNum ? num : String(code)}`
  },

  _formatAreaTypeDisplay(code) {
    if (code === undefined || code === null || code === '') return ''
    const key = String(code).toLowerCase()
    return AREA_TYPE_MAP[key] || String(code)
  },

  _getRegionTypeDisplay(out) {
    if (!out || typeof out !== 'object') return ''

    // 设施：本次需求不改其“弹窗展示”，这里仍保留映射能力以便后续使用
    if (out.is_facility) {
      const facilityCode = out.facility_type ?? out.type ?? (out._raw && out._raw.facility_type)
      return this._formatFacilityTypeDisplay(facilityCode)
    }

    const kind = (out._raw && out._raw.__kind) ? out._raw.__kind : undefined
    const areaType = out.area_type ?? kind

    // 活动区域：显示“活动类型”映射（例如 1 -> 促销活动）
    if (out.is_event || areaType === 'eventarea') {
      const code = out.type_code ?? out.type
      const label = this._formatTypeCodeDisplay(code, EVENT_AREA_TYPE_MAP, '未知活动类型：')
      return label || '活动区域'
    }

    // 其他区域：显示“其他区域类型”映射
    if (!out.is_shop && !out.is_event && !out.is_facility) {
      const code = out.type_code ?? out.type
      if (code !== undefined && code !== null && code !== '') {
        const num = Number(code)
        const hasNum = !Number.isNaN(num) && Number.isFinite(num)
        const key = hasNum ? num : String(code)
        const mapped = OTHER_AREA_TYPE_MAP[key]
        if (mapped) return mapped
        if (hasNum) return `未知类型：${num}`
      }
    }

    // 兜底：显示区域大类
    return this._formatAreaTypeDisplay(areaType || out.type)
  },

  _normalizeRegionForModal(raw) {
    if (!raw || typeof raw !== 'object') return raw
    const src = raw.properties || raw.attributes || raw.store || raw
    const pick = (keys) => {
      for (let k of keys) {
        if (raw[k] !== undefined) return raw[k]
        if (src && src[k] !== undefined) return src[k]
      }
      return undefined
    }
    const out = {}
    out.store_name = pick(['store_name','storeName','shop_name','name','title'])
    out.name = out.store_name || pick(['name','title'])
    out.phone = pick(['phone','phone_number','contact_phone','tel','contact'])
    out.open_time = pick(['open_time','open','business_hours','hours','opening_time'])
    out.close_time = pick(['close_time','close','closing_time'])
    out.description = pick(['description','desc','detail','summary','info'])
    out.type = pick(['type','facility_type','category'])
    out.facility_type = out.type
    out.type_code = pick(['type_code','type_id','event_type','event_type_code','category_code','category_id','other_type','other_type_code','otherarea_type','otherarea_type_code'])
    out.logo_url = pick(['logo_url','image_url','image','logo','thumbnail'])
    out.image_url = out.logo_url
    out.organizer = pick(['organizer','organizer_name','organizerName','owner','owner_name','ownerName','contact_person','contact_name','manager'])
    out.organizer_name = pick(['organizer_name','organizer','organizerName','owner','owner_name','ownerName','manager','contact_person','contact_name'])
    out.organizer_phone = pick(['organizer_phone','organizer_tel','organizer_phone_number','organizer_contact','organizer_contact_phone','organizer_mobile','organizer_mobile_phone','phone','tel','contact'])
    out.contact_person = out.organizer || out.organizer_name
    // area_type/area_type_codes detection
    out.area_type = pick(['area_type','areaType','area_type_code','area_type_codes','facility_type','type'])
    // owner fields for store areas
    out.owner_name = pick(['owner_name','owner','shop_owner','manager_name'])
    out.owner_phone = pick(['owner_phone','owner_tel','owner_phone_number','owner_contact'])
    // determine if this is an event area — prefer explicit kind from hit-testing
    const kind = raw.__kind || (src && src.__kind)
    if (kind === 'eventarea') {
      out.is_event = true
      if (!out.area_type) out.area_type = 'eventarea'
    }

    // determine if this is an event area — require stronger indicators to avoid false positives for facilities
    const explicitEvent = raw.event_id || pick(['is_event','event','activity','activity_id','event_id'])
    const typeLooksLikeEvent = (out.type && /event|activity|eventarea/i.test(String(out.type))) || (out.area_type && /event|activity|eventarea/i.test(String(out.area_type)))
    // also consider area_type codes that equal 'eventarea' or similar
    const areaTypeRaw = (src && (src.area_type || src.areaType || src.area_type_code || src.area_type_codes)) || raw.area_type || raw.areaType
    const areaTypeLooksEvent = areaTypeRaw && /event|activity|eventarea/i.test(String(areaTypeRaw))
    const hasOrganizerAndTime = !!(out.organizer_name && pick(['start','begin','start_time','date','start_time']))
    out.is_event = !!(out.is_event || explicitEvent || typeLooksLikeEvent || areaTypeLooksEvent || hasOrganizerAndTime || raw.is_event)
    // mark facility (point) explicitly to distinguish from polygon areas
    // facilities may be Point or MultiPoint (we draw both)
    const rawGeoType = raw && raw.geometry && raw.geometry.type
    const srcGeoType = src && src.geometry && src.geometry.type
    out.is_facility = (rawGeoType === 'Point' || rawGeoType === 'MultiPoint' || srcGeoType === 'Point' || srcGeoType === 'MultiPoint')
    out.is_shop = !!(out.store_name || out.type === 'store' || out.type === 'shop' || raw.is_shop)
    // include original object for any extra fields
    out._raw = raw
    out.type_display = this._getRegionTypeDisplay(out)
    return out
  },

  _pointInPoly(pt, ring) {
    const x = pt[0], y = pt[1]
    let inside = false
    for (let i=0,j=ring.length-1;i<ring.length;j=i++){
      const xi = ring[i][0], yi = ring[i][1]
      const xj = ring[j][0], yj = ring[j][1]
      const intersect = ((yi>y)!=(yj>y)) && (x < (xj-xi)*(y-yi)/(yj-yi)+xi)
      if (intersect) inside = !inside
    }
    return inside
  },

  // modal close
  closeRegionModal() {
    this._lockScrollTop = null
    this.setData({ showRegionModal: false, activeRegion: null })
  },

  // 跳转到完整活动页
  openActivityList() {
    // activities 在 tabBar 中，使用 switchTab
    wx.switchTab({ url: '/pages/activities/index' })
  },

})