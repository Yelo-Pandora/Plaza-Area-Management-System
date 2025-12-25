const util = require('../../utils/util')

Page({
  data: {
    keyword: '',
    storeResults: [], 
    eventResults: [], 
    searchTypes: ["全部", "活动", "商铺"],
    typeIndex: 0,
    hasSearched: false, // 标记是否执行过搜索动作
    placeholderList: ['搜索商铺或者活动名称', '请输入活动名称', '请输入商铺名称'],
     // 弹窗相关状态
    showModal: false,
    modalType: '', // 'store' 或 'event'
    modalDetail: null,
    modalLoading: false,
    modalRelatedAreas: [], // 仅用于活动详情时展示关联区域
    // 商铺种类映射关系
    storeTypeMap: {
      '0': '其他',
      '1': '美食',
      '2': '影视',
      '3': '服装',
      '4': '游戏',
      '5': '玩具'
    },
  },

  // 辅助工具函数
  parseBool(val) {
    if (val === true || val === 1 || val === '1' || val === 'true') return true;
    return false;
  },
  formatDateStr(s) {
    if (!s) return '';
    if (typeof s === 'string' && s.length >= 16) return s.substr(0, 16);
    return s;
  },
  handleLinkTap(e) {
    const url = e.currentTarget.dataset.url;
    if (!url) return;
    // 逻辑：如果是内部路径（以 /pages 开头），直接跳转
    if (url.startsWith('/pages')) {
      wx.navigateTo({ url });
      return;
    }
    // 逻辑：如果是外部 HTTP/HTTPS 链接，执行复制操作
    wx.setClipboardData({
      data: url,
      success: () => {
        // wx.setClipboardData 默认会弹出一个“内容已复制”的提示
        // 可以追加一个业务提示
        wx.showModal({
          title: '链接已复制',
          content: '外部链接无法直接打开，请复制后在浏览器中粘贴访问。',
          showCancel: false,
          confirmText: '知道了'
        });
      }
    });
  },
  // 辅助函数：判断是否在营业时间内
  getBusinessStatus(openTime, closeTime) {
    if (!openTime || !closeTime) return { label: '未知', isOpen: false };
    var now = new Date();
    var currentMinutes = now.getHours() * 60 + now.getMinutes();
    var openParts = openTime.split(':');
    var openH = parseInt(openParts[0], 10);
    var openM = parseInt(openParts[1], 10);
    var openMinutes = openH * 60 + openM;
    var closeParts = closeTime.split(':');
    var closeH = parseInt(closeParts[0], 10);
    var closeM = parseInt(closeParts[1], 10);
    var closeMinutes = closeH * 60 + closeM;
    var isOpen = false;
    if (closeMinutes > openMinutes) {
      isOpen = currentMinutes >= openMinutes && currentMinutes < closeMinutes;
    } else {
      // 跨天情况
      isOpen = currentMinutes >= openMinutes || currentMinutes < closeMinutes;
    }
    return {
      label: isOpen ? '营业中' : '休息中',
      isOpen: isOpen
    };
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
    if (currentType === '全部' || currentType === '商铺') {
      const storeTask = util.apiRequest(`/search/storearea/search/?name=${encodeURIComponent(kw)}`)
        .then(res => {
          this.setData({ storeResults: res || [] })
        })
        .catch(err => {
          console.error('搜索商铺失败', err)
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

  // 弹窗逻辑
  // 打开商铺详情
  openStore(e) {
    const id = e.currentTarget.dataset.id;
    const item = this.data.storeResults.find(x => x.id === id);
    if (!item) return;
    // 计算营业状态
    const status = this.getBusinessStatus(item.open_time, item.close_time);
    item.statusLabel = status.label;
    item.isOpen = status.isOpen;

    this.setData({
      showModal: true,
      modalType: 'store',
      modalDetail: item,
      modalLoading: false
    });
  },

  // 打开活动详情
  openEvent(e) {
    const id = e.currentTarget.dataset.id;
    const item = this.data.eventResults.find(x => x.id === id);
    if (!item) return;

    this.setData({
      showModal: true,
      modalType: 'event',
      modalDetail: item,
      modalLoading: true,
      modalRelatedAreas: []
    });

    // 获取活动关联的区域列表
    util.apiRequest(`/search/event/${id}/areas/`).then(res => {
      const storeIds = res.storearea_ids || [];
      const eventareaIds = res.eventarea_ids || [];
      const allIds = [...storeIds.map(i => ({id: i, type: 'store'})), ...eventareaIds.map(i => ({id: i, type: 'event'}))];
      
      const fetches = allIds.map(obj => {
        const url = obj.type === 'store' ? `/search/storearea/${obj.id}/` : `/search/eventarea/${obj.id}/`;
        return util.apiRequest(url).catch(() => null);
      });

      return Promise.all(fetches);
    }).then(results => {
      this.setData({
        modalRelatedAreas: results.filter(r => r !== null),
        modalLoading: false
      });
    }).catch(err => {
      console.error('加载关联详情失败', err);
      this.setData({ modalLoading: false });
    });
  },

  closeModal() {
    this.setData({
      showModal: false,
      modalType: '',
      modalDetail: null,
      modalRelatedAreas: []
    });
  },

  // TODO: 以下跳转到地图的接口还需详细修改
  openInMap() {
    const shape = this.data.modalDetail.shape;
    if (!shape) {
      wx.showToast({ title: '该商铺暂无位置数据', icon: 'none' });
      return;
    }
    // 直接存入本地缓存，key 叫 'mapTarget'
    wx.setStorageSync('mapTarget', {
      // type:'store',
      // name: this.data.modalDetail.store_name,
      geometry: shape
    });
    // 跳转到 TabBar 页面
    wx.switchTab({
      url: '/pages/navigation/index',
      fail: (err) => {
        console.error('跳转失败：', err);
      }
    });
  },
})