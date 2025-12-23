const util = require('../../utils/util')

Page({
  data: {
    keyword: '',
    storeResults: [], /* {id: , name: , area_name: } */
    eventResults: [], /* {id: , name: , start_time: , end_time: } */
    searchTypes: ["全部", "活动", "店铺"],
    typeIndex: 0,
    hasSearched: false, // 标记是否执行过搜索动作
    placeholderList: ['搜索店铺或者活动名称', '请输入活动名称', '请输入店铺名称'],
  },

  // 切换搜索类型
  bindTypeChange(e) {
    this.setData({
      typeIndex: e.detail.value,
      hasSearched: false
    })
  },

  onInput(e) {
    this.setData({ keyword: e.detail.value })
    this.setData({ hasSearched: false }) // 用户一旦开始输入，标记为未执行搜索
  },

async doSearch() {
    const kw = (this.data.keyword || '').trim()
    if (!kw) return

    const currentType = this.data.searchTypes[this.data.typeIndex]
    
    // 1. 初始化状态
    this.setData({ 
      storeResults: [], 
      eventResults: [],
      hasSearched: false // 搜索开始前先重置标记
    })
    wx.showLoading({ title: '搜索中...' })

    // 用于存放异步任务的数组
    const tasks = []

    // 2. 根据选中的类型决定调用哪些接口
    if (currentType === '全部' || currentType === '店铺') {
      const storeTask = util.apiRequest(`/search/storearea/search/?name=${encodeURIComponent(kw)}`)
        .then(res => {
          this.setData({ storeResults: res || [] })
        })
        .catch(err => {
          console.error('搜索店铺失败', err)
        })
      tasks.push(storeTask)
    }

    if (currentType === '全部' || currentType === '活动') {
      const eventTask = util.apiRequest(`/search/event/search/?name=${encodeURIComponent(kw)}`)
        .then(res => {
          this.setData({ eventResults: res || [] })
        })
        .catch(err => {
          console.error('搜索活动失败', err)
        })
      tasks.push(eventTask)
    }

    // 3. 等待所有已发出的请求完成
    try {
      await Promise.all(tasks)
    } catch (e) {
      console.error('搜索过程出现错误', e)
    } finally {
      wx.hideLoading()
      this.setData({ hasSearched: true })
    }
  },

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