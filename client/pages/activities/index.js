const util = require('../../utils/util')

Page({
  data: {
    events: [],
    filteredEvents: [],
    eventDetail: null,
    types: [],
    selectedType: '',
    showModal: false,
    modalEvent: null,
    modalArea: null,
    modalLoading: false
  },

  onLoad(options) {
    const event_id = options.event_id
    if (event_id) {
      this.fetchEventDetail(event_id)
    } else {
      this.fetchEventList()
    }
  },

  // 将后端返回的活动对象规范化为页面使用的字段
  normalizeEvent(raw) {
    if (!raw || typeof raw !== 'object') return raw
    const ev = Object.assign({}, raw)
    ev.id = ev.id || ev.event_id || ev.pk || ev.uuid || ev._id
    ev.name = ev.name || ev.event_name || ev.title || ev.eventTitle
    ev.description = ev.description || ev.desc || ev.detail || ev.description_text || ev.summary
    ev.type_name = ev.type_name || ev.type || ev.category || ev.typeName
    // 规范化时间字段，后端可能使用 start_date / start_time / start
    ev.start = ev.start || ev.start_date || ev.start_time || ev.date || ev.begin || ev.startDate || ev.begin_time
    ev.end = ev.end || ev.end_date || ev.end_time || ev.finish || ev.endDate || ev.finish_time
    // 格式化时间显示
    try {
      ev.start = this.formatDateStr(ev.start)
      ev.end = this.formatDateStr(ev.end)
    } catch (e) {}
    return ev
  },

  // 简单格式化时间字符串，显示到分钟
  formatDateStr(s) {
    if (!s) return ''
    try {
      // 如果是类似 'YYYY-MM-DD HH:MM:SS'，取前16位
      if (typeof s === 'string' && s.length >= 16 && s[4] === '-' ) return s.substr(0,16)
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

  applyFilter(typeOrEvent) {
    let type = typeOrEvent
    if (typeof typeOrEvent === 'object' && typeOrEvent.currentTarget) {
      type = typeOrEvent.currentTarget.dataset.type
    }
    const selected = type === this.data.selectedType ? '' : type
    this.setData({ selectedType: selected })
    const list = (this.data.events || []).filter(ev => {
      if (!selected) return true
      return (ev.type_name || '其他') === selected
    })
    this.setData({ filteredEvents: list })
  },

  fetchEventList() {
    wx.showLoading({ title: '加载中...' })
    util.apiRequest('/search/event/list/').then(res => {
      console.log('fetchEventList response:', res)
      let list = []

      // 直接数组
      if (Array.isArray(res)) {
        list = res
      // 常见的命名：events
      } else if (res && Array.isArray(res.events)) {
        list = res.events
      // Django REST Framework 分页格式：{count, next, previous, results: [...]}
      } else if (res && Array.isArray(res.results)) {
        list = res.results
      // 有些后端会把数据放在 data 字段
      } else if (res && res.data) {
        if (Array.isArray(res.data)) list = res.data
        else if (Array.isArray(res.data.results)) list = res.data.results
      } else if (res && typeof res === 'object') {
        // 尝试合并对象中的数组字段（兼容分类返回）
        const arr = []
        Object.keys(res).forEach(k => (res[k] || []).forEach(it => arr.push(it)))
        list = arr
      }

      console.log('parsed event list length:', Array.isArray(list) ? list.length : 0)
      // 规范化每个事件对象，确保 WXML 能正确读取字段
      const normalized = (list || []).map(it => this.normalizeEvent(it))
      // 收集类型并设置默认筛选数据
      const types = Array.from(new Set(normalized.map(e => e.type_name || '其他')))
      this.setData({ events: normalized, types, selectedType: '' })
      // 初始显示全部
      this.setData({ filteredEvents: normalized })
      wx.hideLoading()
    }).catch(err => {
      console.error('获取活动列表失败', err)
      wx.hideLoading()
      wx.showToast({ title: '获取活动列表失败，请检查网络或后端', icon: 'none' })
    })
  },

  fetchEventDetail(id) {
    wx.showLoading({ title: '加载中...' })
    util.apiRequest(`/search/event/${id}/`).then(res => {
      const detail = this.normalizeEvent(res)
      this.setData({ eventDetail: detail })
      wx.hideLoading()
    }).catch(err => {
      console.error('获取活动详情失败', err)
      wx.hideLoading()
      wx.showToast({ title: '获取活动详情失败', icon: 'none' })
    })
  },

  openActivity(e) {
    const id = e.currentTarget.dataset.id
    if (!id) return
    // 在弹窗中显示事件与区域信息
    const ev = (this.data.events || []).find(x => String(x.id) === String(id))
    if (!ev) return
    this.setData({ showModal: true, modalEvent: ev, modalArea: null, modalLoading: true })

    // 如果事件对象自带区域信息，直接使用
    if (ev.area || ev.areas || ev.region || ev.zone) {
      const area = ev.area || (Array.isArray(ev.areas) ? ev.areas[0] : ev.region || ev.zone)
      this.setData({ modalArea: area, modalLoading: false })
      return
    }

    // 否则尝试基于常见字段请求后端获取区域详情
    const areaId = ev.area_id || ev.areaId || ev.region_id || ev.zone_id
    if (!areaId) {
      this.setData({ modalLoading: false })
      return
    }

    const tryEndpoints = [
      `/map/area/${areaId}/`,
      `/search/area/${areaId}/`,
      `/area/${areaId}/`
    ]

    const tryFetch = idx => {
      if (idx >= tryEndpoints.length) {
        this.setData({ modalLoading: false })
        return
      }
      util.apiRequest(tryEndpoints[idx]).then(res => {
        this.setData({ modalArea: res, modalLoading: false })
      }).catch(err => {
        tryFetch(idx+1)
      })
    }

    tryFetch(0)
  },

  closeModal() {
    this.setData({ showModal: false, modalEvent: null, modalArea: null })
  }

})