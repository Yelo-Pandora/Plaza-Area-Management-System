const util = require('../../utils/util')

Page({
  data: {
    store: {},
  },

  onLoad(options) {
    const id = options.store_id || options.id
    if (id) this.fetchStore(id)
  },

  fetchStore(id) {
    util.apiRequest(`/search/storearea/${id}/`).then(res => {
      this.setData({ store: res })
    }).catch(err => {
      console.error('获取店铺详情失败', err)
      wx.showToast({ title: '获取店铺失败', icon: 'none' })
    })
  },

  openOnMap() {
    const mapId = this.data.store.map_id
    if (!mapId) return
    // 跳转到首页的地图展示页或其他实现；此处简单跳转首页
    wx.switchTab({ url: '/pages/home/index' })
  }
})
