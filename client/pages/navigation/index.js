const util = require('../../utils/util')

Page({
  data: {
    start: { x: '', y: '' },
    end: { x: '', y: '' },
    routeResult: null
  },

  onStartX(e) { this.setData({ 'start.x': e.detail.value }) },
  onStartY(e) { this.setData({ 'start.y': e.detail.value }) },
  onEndX(e) { this.setData({ 'end.x': e.detail.value }) },
  onEndY(e) { this.setData({ 'end.y': e.detail.value }) },

  doRoute() {
    const map_id = 1 // 默认 map id，可改为动态选择
    const start = this.data.start
    const end = this.data.end
    if (!start.x || !start.y || !end.x || !end.y) return

    const payload = { map_id, start: { x: parseFloat(start.x), y: parseFloat(start.y) }, end: { x: parseFloat(end.x), y: parseFloat(end.y) } }

    util.apiRequest('/guide/route/', 'POST', payload).then(res => {
      this.setData({ routeResult: res })
    }).catch(err => {
      console.error('路径规划失败', err)
      wx.showToast({ title: '路径规划失败', icon: 'none' })
    })
  }

})