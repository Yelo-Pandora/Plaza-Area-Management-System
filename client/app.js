// app.js
App({
  onLaunch: function () {
    // 小程序启动之后 触发
    console.log('App Launch')
  },
  onShow: function () {
    // 小程序显示
    console.log('App Show')
  },
  onHide: function () {
    // 小程序隐藏
    console.log('App Hide')
  },
  globalData: {
    userInfo: null
  }
})