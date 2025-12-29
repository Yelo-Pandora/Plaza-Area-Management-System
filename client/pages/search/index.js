const util = require('../../utils/util')

Page({
  data: {
    keyword: '',
    storeResults: [],
    eventResults: [],
    searchTypes: ["全部", "活动", "店铺"],
    typeIndex: 0,
    hasSearched: false, // 标记是否执行过搜索动作
    placeholderList: ['搜索店铺或者活动名称', '请输入活动名称', '请输入店铺名称'],
    // 弹窗相关状态
    showModal: false,
    modalType: '', // 'store' 或 'event'
    modalDetail: null,
    modalLoading: false,
    modalRelatedStoreareas: [], // 活动详情，存放关联的店铺区域详情
    modalRelatedEventareas: [], // 活动详情，存放关联的活动区域详情
    modalRelatedEvents: [], // 店铺详情，存放店铺关联的活动列表
    // 店铺种类映射关系
    storeTypeMap: {
      '0': '普通店铺',
      '1': '餐饮',
      '2': '服饰',
      '3': '娱乐',
      '4': '服务'
    },
    eventTypeMap: {
      '0': '通用活动区域',
      '1': '促销活动',
      '2': '展览活动',
      '3': '表演活动',
    },
  },

  // 处理 conf 页面"再次搜索"跳转
  onShow() {
    const tempSearch = wx.getStorageSync('tempSearch');
    if (tempSearch) {
      const { keyword, typeIndex } = tempSearch;
      // 自动填充搜索框内容
      // 自动切换选项菜单项
      this.setData({
        keyword: keyword,
        typeIndex: typeIndex
      }, () => {
        // 自动执行搜索逻辑
        this.doSearch();
      });
      // 清理临时缓存，避免以后点击底部Tab切换回搜索页时重复触发搜索
      wx.removeStorageSync('tempSearch');
    }
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

  // 规范化活动对象
  normalizeEvent(raw) {
    if (!raw) return null;
    const ev = Object.assign({}, raw);
    ev.id = ev.id || ev.event_id;
    ev.event_name = ev.event_name || ev.name;
    ev.is_active = this.parseBool(ev.is_active !== undefined ? ev.is_active : ev.isActive);
    ev.start_date = this.formatDateStr(ev.start_date || ev.start);
    ev.end_date = this.formatDateStr(ev.end_date || ev.end);
    return ev;
  },

  // 为活动填充种类 Label
  async fillEventLabel(ev) {
    if (!ev || !ev.id) return ev;
    try {
      // 额外请求一次关联区域 ID
      const res = await util.apiRequest(`/search/event/${ev.id}/areas/`);
      const eventareaIds = res.eventarea_ids || [];
      if (eventareaIds.length > 0) {
        // 请求第一个活动区域的详情来获取 type
        const areaDetail = await util.apiRequest(`/search/eventarea/${eventareaIds[0]}/`);
        const typeCode = areaDetail.type || 0;
        ev.area_type_label = this.data.eventTypeMap[String(typeCode)] || '其他';
      } else {
        ev.area_type_label = '其他';
      }
    } catch (e) {
      ev.area_type_label = '其他';
    }
    return ev;
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

    // 本地暂存历史记录
    let history = wx.getStorageSync('searchHistory') || [];
    // 过滤完全重复的记录（关键词和类型都一样才算重复）
    history = history.filter(item => !(item.keyword === kw && item.type === currentType));
    // 插入新记录，生成唯一的 id
    history.unshift({
      id: Date.now() + Math.random(), // 唯一标识符，确保每条记录在渲染层唯一
      keyword: kw,
      type: currentType,
      typeIndex: this.data.typeIndex
    });
    if (history.length > 10) history = history.slice(0, 10);
    wx.setStorageSync('searchHistory', history);

    // 1. 初始化状态
    this.setData({
      storeResults: [],
      eventResults: [],
      hasSearched: false // 搜索开始前先重置标记
    })
    wx.showLoading({ title: '搜索中...' })

    try {
      // 用于存放异步任务的列表
      const tasks = [];
      // 搜索店铺
      if (currentType === '全部' || currentType === '店铺') {
        tasks.push(util.apiRequest(`/search/storearea/search/?name=${encodeURIComponent(kw)}`).then(res => {
          this.setData({ storeResults: res || [] });
        }));
      }

      // 搜索活动
      if (currentType === '全部' || currentType === '活动') {
        tasks.push(util.apiRequest(`/search/event/search/?name=${encodeURIComponent(kw)}`).then(async res => {
          let list = res || [];
          // 对搜索结果中的每个活动进行分类补全
          const processedList = await Promise.all(list.map(async it => {
            const normalized = this.normalizeEvent(it);
            return await this.fillEventLabel(normalized);
          }));
          this.setData({ eventResults: processedList });
        }));
      }

      await Promise.all(tasks);
    } catch (e) {
      console.error('搜索失败', e);
    } finally {
      wx.hideLoading();
      this.setData({ hasSearched: true });
    }
  },

  // 弹窗逻辑
  // 打开店铺详情
   async openStore(e) {
    const id = e.currentTarget.dataset.id;
    const item = this.data.storeResults.find(x => x.id === id);
    if (!item) return;

    const status = this.getBusinessStatus(item.open_time, item.close_time);
    item.statusLabel = status.label;
    item.isOpen = status.isOpen;

    this.setData({
      showModal: true,
      modalType: 'store',
      modalDetail: item,
      modalLoading: true,
      modalRelatedEvents: []
    });

    try {
      const res = await util.apiRequest(`/search/storearea/${id}/events/`);
      const eventIds = res.event_ids || [];
      const eventFetches = eventIds.map(async eid => {
        const rawEvent = await util.apiRequest(`/search/event/${eid}/`).catch(() => null);
        if (rawEvent) {
          const normalized = this.normalizeEvent(rawEvent);
          return await this.fillEventLabel(normalized);
        }
        return null;
      });
      const results = await Promise.all(eventFetches);
      this.setData({
        modalRelatedEvents: results.filter(r => r !== null),
        modalLoading: false
      });
    } catch (err) {
      this.setData({ modalLoading: false });
    }
  },

  // 打开活动详情
  async openEvent(e) {
    const id = e.currentTarget.dataset.id;
    let item = this.data.eventResults.find(x => x.id === id);
    if (!item) return;

    // 再次确认补全分类信息
    if (!item.area_type_label) {
      item = await this.fillEventLabel(item);
    }

    this.setData({
      showModal: true,
      modalType: 'event',
      modalDetail: item,
      modalLoading: true,
      modalRelatedStoreareas: [],
      modalRelatedEventareas: []
    });

    try {
      const res = await util.apiRequest(`/search/event/${id}/areas/`);
      const storeIds = res.storearea_ids || [];
      const eventIds = res.eventarea_ids || [];

      const [stores, eventAreas] = await Promise.all([
        Promise.all(storeIds.map(sid => util.apiRequest(`/search/storearea/${sid}/`).catch(() => null))),
        Promise.all(eventIds.map(eid => util.apiRequest(`/search/eventarea/${eid}/`).catch(() => null)))
      ]);

      this.setData({
        modalRelatedStoreareas: stores.filter(r => r !== null),
        modalRelatedEventareas: eventAreas.filter(r => r !== null),
        modalLoading: false
      });
    } catch (err) {
      this.setData({ modalLoading: false });
    }
  },

  closeModal() {
    this.setData({
      showModal: false,
      modalType: '',
      modalDetail: null,
      modalRelatedAreas: []
    });
  },

  // 跳转到地图的函数
  openInMap(e) {
    // 获取参数
    const { shape, type, areaid } = e.currentTarget.dataset;
    if (!shape || !areaid) {
      wx.showToast({ title: '该区域位置数据异常', icon: 'none' });
      return;
    }
    // 调用后端接口获取所在地图的 id
    util.apiRequest(`/search/${type}/${areaid}/map/`).then(res => {
      // 兼容处理返回的 map_id
      const mapId = Array.isArray(res.map_ids) ? res.map_ids[0] : res.map_ids;
      if (!mapId) {
        wx.showToast({ title: '关联地图不存在', icon: 'none' });
        return;
      }
      // 存入本地缓存供 navigation 页面使用
      wx.setStorageSync('mapTarget', {
        geometry: shape,
        mapId: mapId
      });
      // 跳转到导航页面，因为 navigation 是 TabBar 页面，必须使用 switchTab
      wx.switchTab({
        url: '/pages/navigation/index',
        success: () => {
          //console.log('成功跳转至地图页面');
        }
      });
    }).catch(err => {
      console.error('获取地图ID失败', err);
      wx.showToast({ title: '地图定位失败', icon: 'none' });
    });
  },
})