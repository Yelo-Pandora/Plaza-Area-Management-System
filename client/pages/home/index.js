// pages/home/index.js
const util = require('../../utils/util')

Page({
  data: {
    recommended: []
  },

  onLoad(options) {
    this.fetchRecommendations()
  },

  fetchRecommendations() {
    // 调用后端活动列表接口，取得推荐活动（不传 type 时后端按分类返回）
    util.apiRequest('/search/event/list/').then(res => {
      // 如果返回带 'events' 字段，则取它；否则把所有分类合并为一维数组展示
      if (res && res.events) {
        this.setData({ recommended: res.events })
      } else if (res && typeof res === 'object') {
        // 合并分类下的活动
        const arr = []
        Object.keys(res).forEach(k => {
          const list = res[k] || []
          list.forEach(it => arr.push(it))
        })
        this.setData({ recommended: arr })
      }
    }).catch(err => {
      console.error('获取推荐活动失败', err)
    })
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
  }

})