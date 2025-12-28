// pages/conf/index.js
Page({
  data: {
    loggedIn: false,
    profile: {},
    tempAvatarUrl: '', // 临时头像
    tempNickName: '',  // 临时昵称
    login: { account: '', password: '' },
    searchHistory : [], // 本地暂存的搜索历史记录
  },

  onLoad(options) {
    this.refreshData();
  },

  onShow() {
    this.refreshData();
  },

  // 封装数据刷新逻辑
  refreshData() {
    const p = wx.getStorageSync('wxProfile') || null;
    const history = wx.getStorageSync('searchHistory') || [];
    this.setData({ 
      loggedIn: !!p, 
      profile: p || {},
      searchHistory: history
    });
  },

  // 清空搜索历史
  clearHistory() {
    const self = this;
    wx.showModal({
      title: '提示',
      content: '确定清空所有搜索历史吗？',
      success(res) {
        if (res.confirm) {
          wx.removeStorageSync('searchHistory');
          self.setData({ searchHistory: [] });
        }
      }
    });
  },

  // 复制内容
  copyKeyword(e) {
    const text = e.currentTarget.dataset.text;
    wx.setClipboardData({
      data: text,
      success: () => wx.showToast({ title: '搜索记录已复制' })
    });
  },

  // 再次搜索
  reSearch(e) {
    const item = e.currentTarget.dataset.item;
    // 逻辑：跳转到搜索页，并通过缓存或全局变量传递参数
    // 这里简单处理：为了让search页面知道要搜什么，我们可以存一个临时值
    wx.setStorageSync('tempSearch', item); 
    wx.switchTab({
      url: '/pages/search/index'
    });
  },

  // 删除单条记录
  deleteOneHistory(e) {
    const index = e.currentTarget.dataset.index;
    // 防错检查
    if (typeof index !== 'number') return;
    // 获取当前数据副本
    let history = [...this.data.searchHistory];
    // 仅删除指定索引的那一条
    history.splice(index, 1);
    // 同步到视图和缓存
    this.setData({
      searchHistory: history
    });
    wx.setStorageSync('searchHistory', history);
    wx.showToast({ title: '已删除', icon: 'none' });
  },

  onAccount(e) { this.setData({ 'login.account': e.detail.value }) },
  onPassword(e) { this.setData({ 'login.password': e.detail.value }) },

  // 选择头像回调
  onChooseAvatar(e) {
    const { avatarUrl } = e.detail;
    this.setData({ tempAvatarUrl: avatarUrl });
  },

  // 昵称输入
  onNicknameInput(e) {
    this.setData({ tempNickName: e.detail.value });
  },

  // 昵称失焦（部分机型 nickname 只有失焦能拿到）
  onNicknameBlur(e) {
    this.setData({ tempNickName: e.detail.value });
  },

  doLogin() {
    const { tempAvatarUrl, tempNickName } = this.data;
    if (!tempAvatarUrl || tempAvatarUrl === '') {
      return wx.showToast({ title: '请选择头像', icon: 'none' });
    }
    if (!tempNickName) {
      return wx.showToast({ title: '请输入昵称', icon: 'none' });
    }
    wx.showLoading({ title: '登录中...' });
    // 此时调用 wx.login
    wx.login({
      success: (res) => {
        const userInfo = {
          avatarUrl: tempAvatarUrl,
          nickName: tempNickName,
          signature: "微信用户"
        };
        // 存入本地缓存
        wx.setStorageSync('wxProfile', userInfo);
        this.setData({
          loggedIn: true,
          profile: userInfo
        });
        wx.hideLoading();
        wx.showToast({ title: '欢迎回来！' });
      }
    });
  },

  doLogout() {
    wx.removeStorageSync('wxProfile')
    this.setData({ loggedIn: false, profile: {}, login: { account: '', password: '' } })
    wx.showToast({ title: '已登出', icon: 'success' })
  },

  confirmLogout() {
    const self = this
    wx.showModal({
      title: '确认退出登录',
      content: '确定要退出登录吗？',
      confirmText: '退出',
      cancelText: '取消',
      success(res) {
        if (res.confirm) {
          self.doLogout()
        }
      }
    })
  },
})