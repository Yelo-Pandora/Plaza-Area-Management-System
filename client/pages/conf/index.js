// pages/conf/index.js
Page({
  data: {
    loggedIn: false,
    profile: {},
    login: { account: '', password: '' }
  },

  onLoad(options) {
    const p = wx.getStorageSync('wxProfile') || null
    if (p) this.setData({ loggedIn: true, profile: p })
  },

  onShow() {
    const p = wx.getStorageSync('wxProfile') || null
    if (p) this.setData({ loggedIn: true, profile: p })
  },

  onAccount(e) { this.setData({ 'login.account': e.detail.value }) },
  onPassword(e) { this.setData({ 'login.password': e.detail.value }) },

  doLogin() {
    // 使用微信授权获取用户信息（仅本地存储）
    if (wx.getUserProfile) {
      wx.getUserProfile({
        desc: '用于登录并显示个人信息',
        success: (res) => {
          const user = res.userInfo
          wx.setStorageSync('wxProfile', user)
          this.setData({ loggedIn: true, profile: user })
          wx.showToast({ title: '登录成功' })
        },
        fail: () => {
          wx.showToast({ title: '授权失败', icon: 'none' })
        }
      })
    } else {
      // 兼容旧版
      wx.getUserInfo({
        success: (res) => {
          const user = res.userInfo
          wx.setStorageSync('wxProfile', user)
          this.setData({ loggedIn: true, profile: user })
          wx.showToast({ title: '登录成功' })
        },
        fail: () => wx.showToast({ title: '授权失败', icon: 'none' })
      })
    }
  },

  doLogout() {
    wx.removeStorageSync('wxProfile')
    this.setData({ loggedIn: false, profile: {}, login: { account: '', password: '' } })
    wx.showToast({ title: '已登出', icon: 'success' })
  },

  openFavorites() { wx.showToast({ title: '我的收藏（占位）', icon: 'none' }) },
  openMyEvents() { wx.showToast({ title: '我的活动（占位）', icon: 'none' }) },
  openSettings() { wx.showToast({ title: '设置（占位）', icon: 'none' }) }

})