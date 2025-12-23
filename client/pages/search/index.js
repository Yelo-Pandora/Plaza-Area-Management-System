const util = require('../../utils/util')

Page({
  data: {
    keyword: '',
    storeResults: [],
    eventResults: []
  },

  onInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  doSearch() {
    const kw = (this.data.keyword || '').trim()
    if (!kw) return

    // 搜索店铺
    util.apiRequest(`/search/storearea/search/?name=${encodeURIComponent(kw)}`).then(res => {
      this.setData({ storeResults: res || [] })
    }).catch(err => console.error('搜索店铺失败', err))

    // 搜索活动
    util.apiRequest(`/search/event/search/?name=${encodeURIComponent(kw)}`).then(res => {
      this.setData({ eventResults: res || [] })
    }).catch(err => console.error('搜索活动失败', err))
  }

  ,

  openStore(e) {
    const id = e.currentTarget.dataset.id
    if (!id) return
    wx.navigateTo({ url: `/pages/store/index?store_id=${id}` })
  },

  openEvent(e) {
    const id = e.currentTarget.dataset.id
    if (!id) return
    wx.navigateTo({ url: `/pages/activities/index?event_id=${id}` })
  }

})