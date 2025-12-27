const util = require('../../utils/util')

Page({
  data: {
    events: [],
    filteredEvents: [],
    eventDetail: null,
    types: [],
    selectedType: '',
    // 弹窗相关状态
    showModal: false,
    modalEvent: null,
    modalAreas: [],
    modalLoading: false
  },

  onLoad: function(options) {
    const event_id = options.event_id
    if (event_id) {
      this.fetchEventDetail(event_id)
    } else {
      this.fetchEventList()
    }
  },

  // 将后端返回的活动对象规范化为页面使用的字段
  parseBool: function(val) {
    if (val === true) return true
    if (val === false) return false
    if (val === 1 || val === '1') return true
    if (val === 0 || val === '0') return false
    if (typeof val === 'string') {
      const v = val.trim().toLowerCase()
      return ['true', '1', 'yes', 'on'].includes(v)
    }
    return false
  },

  normalizeEvent: function(raw) {
    if (!raw || typeof raw !== 'object') return raw
    const ev = Object.assign({}, raw)
    ev.id = ev.id || ev.event_id || ev.pk || ev.uuid || ev._id
    ev.name = ev.name || ev.event_name || ev.title || ev.eventTitle
    ev.description = ev.description || ev.desc || ev.detail || ev.description_text || ev.summary
    // 规范 is_active 字段（兼容 is_active / isActive / active / '1' 等）
    ev.is_active = this.parseBool(ev.is_active !== undefined ? ev.is_active : (ev.isActive !== undefined ? ev.isActive : ev.active))
    ev.type_name = ev.type_name || ev.type || ev.category || ev.typeName
    // 规范化时间字段，后端可能使用 start_date / start_time / start
    ev.start = ev.start || ev.start_date || ev.start_time || ev.date || ev.begin || ev.startDate || ev.begin_time
    ev.end = ev.end || ev.end_date || ev.end_time || ev.finish || ev.endDate || ev.finish_time
    // 保留原始时间以便比较，然后格式化用于显示
    ev._raw_end = ev.end
    // 计算活动是否处于进行中（基于结束时间）
    try {
      ev.is_ongoing = this.isOngoing(ev._raw_end)
      ev.status_label = ev.is_ongoing ? '进行中' : '已截止'
    } catch (e) {
      ev.is_ongoing = false
      ev.status_label = '已截止'
    }
    // 格式化时间显示
    try {
      ev.start = this.formatDateStr(ev.start)
      ev.end = this.formatDateStr(ev.end)
    } catch (e) {}
    return ev
  },

  // 判断给定时间（字符串或时间值）是否晚于当前时间
  isOngoing: function(endVal) {
    if (!endVal) return false
    try {
      let d
      if (typeof endVal === 'string') {
        // 兼容 'YYYY-MM-DD HH:MM:SS' 格式
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

  // 简单格式化时间字符串，显示到分钟
  formatDateStr: function(s) {
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

  applyFilter: function(typeOrEvent) {
    let type = typeOrEvent
    if (typeof typeOrEvent === 'object' && typeOrEvent.currentTarget) {
      type = typeOrEvent.currentTarget.dataset.type
    }
    const selected = type === this.data.selectedType ? '' : type
    this.setData({ selectedType: selected })
    const list = (this.data.events || []).filter(ev => {
      if (!selected) return true
      // 如果 types 是基于关联区域的 type 值，则 ev.area_type_codes 保存了关联区域的 type 值数组
      if (selected === 'other') {
        return !(ev.area_type_codes && ev.area_type_codes.length)
      }
      if (Array.isArray(ev.area_type_codes) && ev.area_type_codes.length) {
        return ev.area_type_codes.includes(String(selected)) || ev.area_type_codes.includes(Number(selected))
      }
      // 兜底：仍保留按事件自身 type_name 的筛选（兼容老数据）
      return (ev.type_name || '其他') === selected
    })
    this.setData({ filteredEvents: list })
  },

  fetchEventList: function() {
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

      // 先设置 events 与初始显示
      this.setData({ events: normalized, selectedType: '' })
      this.setData({ filteredEvents: normalized })

      // 为了按关联区域的 `type` 属性分类筛选，需要请求每个事件的关联区域ID列表，
      // 再请求每个区域的详情以获取区域的 `type` 字段。
      // 为减少重复请求，使用 areaCache 缓存已请求的区域详情（按 id）。
      const areaCache = {}
      const areaFetches = (normalized || []).map(ev => {
        const id = ev && ev.id
        if (!id) return Promise.resolve(null)
        return util.apiRequest(`/search/event/${id}/areas/`).catch(() => null)
      })

      Promise.all(areaFetches).then(results => {
        // 对每个事件，按 storearea_ids / eventarea_ids 请求对应区域详情（并缓存）
        const detailFetches = []
        results.forEach((r, idx) => {
          const ev = normalized[idx]
          ev.area_type_codes = []
          if (!r) return
          const storeIds = r.storearea_ids || []
          const eventareaIds = r.eventarea_ids || []
            // 仅请求并使用 eventarea 的 type 字段作为分类标准（忽略 storearea）
            const idsEventarea = eventareaIds || []
            idsEventarea.forEach(idVal => {
              const cacheKey = `eventarea:${idVal}`
              if (areaCache[cacheKey]) {
                const areaTypeVal = areaCache[cacheKey].type || areaCache[cacheKey].type_id || areaCache[cacheKey].typeCode || areaCache[cacheKey].typeId
                if (areaTypeVal !== undefined && areaTypeVal !== null) ev.area_type_codes.push(String(areaTypeVal))
                return
              }
              const p = util.apiRequest(`/search/eventarea/${idVal}/`).then(detail => {
                if (detail) {
                  areaCache[cacheKey] = detail
                  const areaTypeVal = detail.type || detail.type_id || detail.typeCode || detail.typeId || detail.type
                  if (areaTypeVal !== undefined && areaTypeVal !== null) ev.area_type_codes.push(String(areaTypeVal))
                }
              }).catch(() => { /* ignore single area failure */ })
              detailFetches.push(p)
            })
        })

        return Promise.all(detailFetches).then(() => ({ normalized, areaCache }))
      }).then(({ normalized }) => {
        // 生成顶部筛选 types：基于收集到的 area_type_codes 映射为 label
        const areaTypeSet = new Set()
        normalized.forEach(ev => {
          (ev.area_type_codes || []).forEach(t => areaTypeSet.add(String(t)))
        })

        // 示例映射：可按需调整或从后端获取更准确的映射
        const areaTypeLabelMap = { '1': '促销活动', '2': '品牌活动', '3': '主题活动', '4': '会员活动', '5': '其他' }
        const types = Array.from(areaTypeSet).map(k => ({ key: k, label: areaTypeLabelMap[k] || `类型 ${k}` }))

        // 若存在没有任何 eventarea type 的活动，则加入一个 "其他" 筛选项（key: 'other'）
        const hasOther = normalized.some(ev => !(ev.area_type_codes && ev.area_type_codes.length))
        if (hasOther) types.push({ key: 'other', label: '其他' })

        // 为每个事件设置显示用的 label（优先使用收集到的 eventarea type 的第一个映射）
        normalized.forEach(ev => {
          if (Array.isArray(ev.area_type_codes) && ev.area_type_codes.length) {
            const k = String(ev.area_type_codes[0])
            ev.area_type_label = areaTypeLabelMap[k] || (`类型 ${k}`)
          } else {
            // 回退到事件自身的 type_name 或 '其他'
            ev.area_type_label = ev.type_name || '其他'
          }
        })

        this.setData({ events: normalized, types })
        wx.hideLoading()
      }).catch(err => {
        console.error('获取区域详情失败', err)
        wx.hideLoading()
      })
    }).catch(err => {
      console.error('获取活动列表失败', err)
      wx.hideLoading()
      wx.showToast({ title: '获取活动列表失败，请检查网络或后端', icon: 'none' })
    })
  },

  fetchEventDetail: function(id) {
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

  openActivity: function(e) {
    const id = e.currentTarget.dataset.id
    if (!id) return
    const ev = (this.data.events || []).find(x => String(x.id) === String(id))
    if (!ev) return
    // 规范 modalEvent 的 is_active 字段（兼容 isActive）
    ev.is_active = (ev.is_active !== undefined) ? ev.is_active : ((ev.isActive !== undefined) ? ev.isActive : false)
    this.setData({ showModal: true, modalEvent: ev, modalAreas: [], modalLoading: true })

    // 首先获取该活动关联的区域ID列表
    util.apiRequest(`/search/event/${id}/areas/`).then(res => {
      const storeIds = res.storearea_ids || []
      const eventareaIds = res.eventarea_ids || []

      const storeFetches = (storeIds || []).map(i => util.apiRequest(`/search/storearea/${i}/`).catch(() => null))
      const eventareaFetches = (eventareaIds || []).map(i => util.apiRequest(`/search/eventarea/${i}/`).catch(() => null))

      // 返回 results 并携带 storeIds 长度以便区分前半部分为 storearea
      return Promise.all([...storeFetches, ...eventareaFetches]).then(results => ({ results, storeCount: storeIds.length }))
    }).then(({ results, storeCount }) => {
      const areas = []
      results.forEach((r, idx) => {
        if (!r) return
        const areaType = idx < storeCount ? 'storearea' : 'eventarea'
        // 规范 is_active 字段，使用 parseBool 以兼容多种后端返回格式
        const rawActive = (r.is_active !== undefined) ? r.is_active : (r.isActive !== undefined ? r.isActive : (r.active !== undefined ? r.active : false))
        const isActive = this.parseBool(rawActive)
        const item = Object.assign({ area_type: areaType, is_active: isActive }, r)
        // 归一化店铺相关字段，兼容后端可能的命名差异
        item.owner_name = r.owner_name || r.owner || r.ownerName || r.shop_owner || r.shopOwner || r.keeper || ''
        item.owner_phone = r.owner_phone || r.ownerPhone || r.contact_phone || r.contact || r.phone || r.mobile || ''
        // 优先使用 open_time / close_time 字段，并生成显示文本 open - close
        const openTime = r.open_time || r.openTime || r.open || r.opening_time || r.open_from || ''
        const closeTime = r.close_time || r.closeTime || r.close || r.closing_time || r.open_to || ''
        item.open_time = openTime
        item.close_time = closeTime
        if (openTime && closeTime) {
          item.business_hours = openTime + ' - ' + closeTime
        } else if (openTime) {
          item.business_hours = openTime
        } else if (closeTime) {
          item.business_hours = closeTime
        } else {
          item.business_hours = r.business_hours || r.opening_hours || r.hours || r.businessHours || ''
        }
        areas.push(item)
      })
      this.setData({ modalAreas: areas, modalLoading: false })
    }).catch(err => {
      console.error('获取活动关联区域失败', err)
      this.setData({ modalLoading: false })
    })
  },

  closeModal: function() {
    this.setData({ showModal: false, modalEvent: null, modalAreas: [], modalLoading: false })
  },

  // 弹窗相关功能已移除
})