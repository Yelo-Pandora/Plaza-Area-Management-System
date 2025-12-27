const util = require('../../utils/util')

Page({
  data: {
    maps: [],
    selectedMapIndex: 0,
    scale: 1,
    offsetX: 0,
    offsetY: 0,
    showRegionModal: false,
    activeRegion: null,
    showZoomPercent: false,
    zoomPercent: 100,
    // 导航相关数据
    selectionMode: null, // 'start' | 'end' | null
    startPoint: null,    // {x, y} 地图地理坐标
    endPoint: null,      // {x, y} 地图地理坐标
    routePoints: [],      // 存储导航路径坐标点 [[x,y], [x,y]...]
    targetHighlightRings: null, // 存储需要高亮的形状数据
    // 店铺区域种类映射
    storeareaTypeMap: {
      '0': '普通店铺',
      '1': '餐饮',
      '2': '服饰',
      '3': '娱乐',
      '4': '服务'
    },
    // 活动区域种类映射
    eventareaTypeMap: {
      '0': '通用活动区域',
      '1': '促销活动',
      '2': '展览活动',
      '3': '表演活动',
    },
    // 其他区域种类映射
    otherareaTypeMap: {
      '0': '公共区域',
      '1': '🚻卫生间',
      '2': '🛗电梯间',
      '3': '其他'
    },
    // 设施种类映射
    facilityTypeMap: {
      '0': '电动扶梯',
      '1': '灭火器',
      '2': '安全出口',
      '3': '服务台',
      '4': '其他'
    },
  },

  onLoad(options) {
    this.fetchMaps()
  },

  // 使用 onShow 捕获从搜索页传来的跳转需求
  onShow() {
    const target = wx.getStorageSync('mapTarget');
    if (target) {
      // 1. 解析 WKT 形状
      const rings = this._parseWKT(target.geometry);
      const targetMapId = target.mapId;
      this.setData({
        targetHighlightRings: rings
      });
      // 2. 尝试切换地图
      if (this.data.maps && this.data.maps.length > 0) {
        // 如果地图列表已存在，直接寻找索引并切换
        this._switchToTargetMap(targetMapId);
      } else {
        // 如果列表还没加载出来，首次进页面，暂存 mapId，由 fetchMaps 加载完后处理
        this._pendingMapId = targetMapId;
      }
      // 清除缓存防止重复触发
      wx.removeStorageSync('mapTarget');
    }
  },

  //内部辅助：根据 mapId 寻找并切换 selectedMapIndex
  _switchToTargetMap(mapId) {
    const idx = this.data.maps.findIndex(m => m.id == mapId); // 使用 == 兼容字符串/数字比较
    if (idx !== -1) {
      if (idx === this.data.selectedMapIndex) {
        // 如果已经在当前页，直接重绘以显示高亮
        this.drawMap();
      } else {
        // 切换楼层
        this.setData({
          selectedMapIndex: idx,
          scale: 1, offsetX: 0, offsetY: 0,
          activeRegion: null,
          startPoint: null,
          endPoint: null,
          routePoints: []
        });
        this.loadMapDetail(idx);
      }
    }
  },

  // 解析 WKT 字符串函数
  _parseWKT(wkt) {
    if (!wkt || typeof wkt !== 'string') return null;
    try {
      // 去掉 SRID 部分，只留 POLYGON ((...)) 或 MULTIPOLYGON (((...)))
      const rawWkt = wkt.indexOf(';') > -1 ? wkt.split(';')[1] : wkt;
      const type = rawWkt.match(/^(POLYGON|MULTIPOLYGON)/i)[0].toUpperCase();
      // 提取括号内的内容
      const content = rawWkt.substring(rawWkt.indexOf('('));
      let rings = [];
      if (type === 'POLYGON') {
        // 格式: ((x y, x y), (x y)) -> 拆分成 ["x y, x y", "x y"]
        const ringsStr = content.slice(2, -2).split('), (');
        rings = ringsStr.map(r => this._wktPointsToCoords(r));
      } 
      else if (type === 'MULTIPOLYGON') {
        // 格式: (((x y, x y)), ((x y))) -> 拆分成多边形，再拆分成环
        const polysStr = content.slice(3, -3).split(')), ((');
        polysStr.forEach(p => {
          const rs = p.split('), (').map(r => this._wktPointsToCoords(r));
          rings = rings.concat(rs);
        });
      }
      return rings;
    } catch (e) {
      console.error('WKT解析失败:', e, wkt);
      return null;
    }
  },
  // 内部辅助：将 "22.5 2.5, 37.5 2.5" 转换为 [[22.5, 2.5], [37.5, 2.5]]
  _wktPointsToCoords(str) {
    return str.split(',').map(pair => {
      const parts = pair.trim().split(/\s+/);
      return [parseFloat(parts[0]), parseFloat(parts[1])];
    });
  },

  // 地图列表与详情加载
  fetchMaps() {
    util.apiRequest('/maps/').then(res => {
      const maps = (res || []).map(m => ({ 
        id: m.id, 
        label: `${m.building_name || ''} ${m.floor_number} 层`, 
        raw: m 
      }))
      this.setData({ maps })
      if (maps.length) {
        let targetIdx = 0;
        // 检查是否有搜索页传来的待跳转 mapId
        if (this._pendingMapId) {
          const idx = maps.findIndex(m => m.id == this._pendingMapId);
          if (idx !== -1) {
            targetIdx = idx;
          }
          this._pendingMapId = null; // 处理完即销毁
        }
        this.loadMapDetail(targetIdx);
      }
    }).catch(err => console.error('加载地图列表失败', err))
  },

  onMapChange(e) {
    const idx = parseInt(e.detail.value, 10) || 0
    this.setData({ 
      selectedMapIndex: idx, 
      scale: 1, 
      offsetX: 0, 
      offsetY: 0, 
      activeRegion: null,
      startPoint: null,
      endPoint: null,
      selectionMode: null,
      routePoints: [],
      targetHighlightRings: null
    })
    this.loadMapDetail(idx)
  },

  loadMapDetail(index) {
    const map = this.data.maps[index]
    if (!map) return
    util.apiRequest(`/maps/${map.id}/`).then(res => {
      // 预计算逻辑开始，为了地图放大到一定比例显示名称
      const regionKeys = ['stores', 'other_areas', 'events'];
      regionKeys.forEach(key => {
        if (res[key] && Array.isArray(res[key])) {
          res[key].forEach(item => {
            // 将计算好的地理坐标中心点存入 item._center
            item._center = this._calculateCenter(item.geometry);
          });
        }
      });
      // 预计算逻辑结束
      const maps = this.data.maps.slice()
      maps[index].raw = res
      this.setData({ maps })
      setTimeout(() => this.drawMap(), 50)
    }).catch(err => console.error('加载地图详情失败', err))
  },

  // 辅助函数：根据 Geometry 粗略地计算估计的中心点，只是为了地图放大到一定比例显示名称
  _calculateCenter(geometry) {
    if (!geometry || !geometry.coordinates) return null;
    
    let rings = [];
    if (geometry.type === 'Polygon') {
      rings = [geometry.coordinates[0]]; // 取外轮廓
    } else if (geometry.type === 'MultiPolygon') {
      rings = [geometry.coordinates[0][0]]; // 取第一个多边形的外轮廓
    }

    if (rings.length === 0 || !rings[0].length) return null;

    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    rings[0].forEach(pt => {
      const x = pt[0], y = pt[1];
      if (x < minX) minX = x; if (x > maxX) maxX = x;
      if (y < minY) minY = y; if (y > maxY) maxY = y;
    });

    return {
      x: (minX + maxX) / 2,
      y: (minY + maxY) / 2
    };
  },

  // 导航功能函数
  toggleSelectStart() {
    if (this.data.selectionMode === 'start') {
      this.setData({ selectionMode: null })
    } else {
      this.setData({ selectionMode: 'start' })
    }
  },

  toggleSelectEnd() {
    if (this.data.selectionMode === 'end') {
      this.setData({ selectionMode: null })
    } else {
      this.setData({ selectionMode: 'end' })
    }
  },

  resetNav() {
    this.setData({
      startPoint: null,
      endPoint: null,
      selectionMode: null,
      routePoints: [], // 清空路径
      targetHighlightRings: null // 清除高亮
    }, () => this.drawMap())
  },

  doNavigation() {
    const { startPoint, endPoint, maps, selectedMapIndex } = this.data;
    if (!startPoint || !endPoint) {
      wx.showToast({ title: '请先选择起终点', icon: 'none' });
      return;
    }
    const mapId = maps[selectedMapIndex].id;
    wx.showLoading({ title: '路线规划中...' });
    // 构造请求参数
    const params = {
      map_id: mapId,
      start: { x: startPoint.x, y: startPoint.y },
      end: { x: endPoint.x, y: endPoint.y }
    };
    console.log('导航请求参数:', params)
    // 调用接口 (注意：根据 util.js 封装，需要指定 'POST')
    util.apiRequest('/guide/route/','POST', params).then(res => {
      wx.hideLoading();
      if (res && res.route && res.route.coordinates) {
        this.setData({
          routePoints: res.route.coordinates
        }, () => {
          // 请求成功后重新触发绘制
          this.drawMap();
          wx.showToast({ title: `全程约 ${res.distance.toFixed(2)} 米`, icon: 'none' });
        });
      } else {
        wx.showToast({ title: '未找到可行路线', icon: 'none' });
      }
    }).catch(err => {
      wx.hideLoading();
      console.error('导航请求失败', err);
      wx.showToast({ title: '导航服务异常', icon: 'none' });
    });
  },

  // 校验点击位置是否为障碍物
  _isValidWalkable(gx, gy) {
    const d = this._drawn
    if (!d) return false
    // 1. 基础轮廓校验：必须在底图轮廓内，且不在镂空内
    let inBase = false
    for (const poly of d.polygons) {
      // poly[0] 是外轮廓
      if (this._pointInPoly([gx, gy], poly[0])) {
        let inHole = false
        // poly[1...] 是内部镂空孔洞
        for (let i = 1; i < poly.length; i++) {
          if (this._pointInPoly([gx, gy], poly[i])) {
            inHole = true; break
          }
        }
        if (!inHole) { inBase = true; break }
      }
    }
    if (!inBase) return false
    // 2. 区域障碍校验：如果在商店、活动区域等特定多边形内，视为障碍
    for (const r of d.regions) {
      if (this._pointInPoly([gx, gy], r.coords[0])) return false
    }
    // 3. 设施点障碍校验：后端寻路算法，设施点周围 0.5 米范围内视为障碍物
    // 但是前端这里为了明显，设施点周围 1 米范围内不可点击
    const OBSTACLE_RADIUS_METERS = 1
    if (d.facilities && d.facilities.length) {
      for (let i = 0; i < d.facilities.length; i++) {
        const f = d.facilities[i]
        try {
          // 获取设施的地理坐标 [x, y]
          const coords = f.geometry.type === 'Point' 
            ? f.geometry.coordinates 
            : (f.geometry.coordinates && f.geometry.coordinates[0])
          
          if (!coords) continue

          // 计算点击位置 (gx, gy) 与设施位置 (coords[0], coords[1]) 的欧几里得距离
          // 因为 SRID:2385 是投影坐标系，单位是米，直接使用勾股定理即可
          const dx = gx - coords[0]
          const dy = gy - coords[1]
          const distance = Math.sqrt(dx * dx + dy * dy)

          if (distance < OBSTACLE_RADIUS_METERS) {
            console.log('点击点距离设施太近，视为障碍:', f.id)
            return false
          }
        } catch (e) {
          console.error('设施距离校验异常', e)
        }
      }
    }
    return true
  },

  // 核心绘制
  drawMap() {
    const idx = this.data.selectedMapIndex
    const map = this.data.maps[idx]
    if (!map || !map.raw) return

    const detail = map.raw.detail_geojson
    const ctx = wx.createCanvasContext('mapCanvas', this)
    const query = wx.createSelectorQuery().in(this)

    query.select('.map-canvas').boundingClientRect(rect => {
      this._canvasRect = rect
      const w = rect.width, h = rect.height
      ctx.clearRect(0, 0, w, h)

      if (!detail) {
        ctx.setFillStyle('#f5f5f5'); ctx.fillRect(0,0,w,h); ctx.draw(); return
      }

      const polygons = []
      if (detail.type === 'GeometryCollection' && Array.isArray(detail.geometries)) {
        detail.geometries.forEach(g => {
          if (g.type === 'Polygon') polygons.push(g.coordinates)
          if (g.type === 'MultiPolygon') g.coordinates.forEach(c => polygons.push(c))
        })
      } else if (detail.type === 'Polygon') polygons.push(detail.coordinates)

      let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
      polygons.forEach(poly => {
        poly.forEach(ring => ring.forEach(pt => {
          const x = pt[0], y = pt[1]
          if (x < minX) minX = x; if (y < minY) minY = y
          if (x > maxX) maxX = x; if (y > maxY) maxY = y
        }))
      })

      const mapW = maxX - minX || 1, mapH = maxY - minY || 1
      const baseScale = Math.min(w / mapW, h / mapH)
      const s = baseScale * this.data.scale

      const toCanvas = (x,y) => {
        const cx = (x - minX) * s + this.data.offsetX + (w - mapW * s)/2
        const cy = (y - minY) * s + this.data.offsetY + (h - mapH * s)/2
        return [cx, cy]
      }

      // 绘制背景/轮廓
      ctx.setStrokeStyle('#333'); ctx.setLineWidth(1); ctx.setFillStyle('#fff')
      polygons.forEach(poly => {
        ctx.beginPath() // 每个 Polygon 开启一个新路径
        // poly 是一个数组：[外轮廓, 孔洞1, 孔洞2...]
        poly.forEach((ring, ri) => {
          ring.forEach((pt, i) => {
            const [cx, cy] = toCanvas(pt[0], pt[1])
            if (i === 0) ctx.moveTo(cx, cy)
            else ctx.lineTo(cx, cy)
          })
          ctx.closePath() // 必须在这里！每个 Ring 绘制完立刻关闭，形成闭合子路径
        })
        // 当一个路径包含多个闭合子路径时，Canvas 使用非零环绕原则实现镂空
        ctx.fill()
        ctx.stroke()
      })
      // polygons.forEach(poly => {
      //   poly.forEach(ring => ring.forEach((pt, i) => {
      //     const [cx, cy] = toCanvas(pt[0], pt[1])
      //     if (i === 0) ctx.moveTo(cx, cy); else ctx.lineTo(cx, cy)
      //   }))
      //   ctx.closePath(); ctx.fill(); ctx.stroke()
      // })

      // 绘制区域颜色
      const regions = []
      const pushRegion = (list, color, kind) => {
        (list || []).forEach(it => {
          if (!it.geometry) return
          const g = it.geometry
          if (g.type === 'Polygon') regions.push({ coords: g.coordinates, meta: it, color, kind })
          else if (g.type === 'MultiPolygon') g.coordinates.forEach(c => regions.push({ coords: c, meta: it, color, kind }))
        })
      }
      pushRegion(map.raw.stores, 'rgba(0,120,212,0.3)', 'storearea')
      pushRegion(map.raw.other_areas, 'rgba(120,200,80,0.3)', 'otherarea')
      pushRegion(map.raw.events, 'rgba(220,80,80,0.3)', 'eventarea')

      regions.forEach(r => {
        ctx.setFillStyle(r.color); ctx.beginPath()
        r.coords.forEach(ring => ring.forEach((pt, i) => {
          const [cx, cy] = toCanvas(pt[0], pt[1])
          if (i===0) ctx.moveTo(cx, cy); else ctx.lineTo(cx, cy)
        }))
        ctx.closePath(); ctx.fill()
      })

      // --- 区域名称绘制逻辑 ---
      if (this.data.scale > 2.4) {
        // 1. 设置文字全局样式
        ctx.setFontSize(10); 
        ctx.setFillStyle('#333333'); // 文字颜色
        ctx.setTextAlign('center');
        ctx.setTextBaseline('middle');

        regions.forEach(r => {
          const meta = r.meta;
          // 获取预计算好的中心点地理坐标
          if (meta && meta._center) {
            let name = ''
            // 获取名称
            if (r.kind === 'storearea') name = meta.store_name;
            else if (r.kind === 'eventarea') name = this.data.eventareaTypeMap[meta.type];
            else if (r.kind === 'otherarea') name = this.data.otherareaTypeMap[meta.type];
            if (name) {
              // 将地理中心点转换为当前画布的像素坐标
              const [tx, ty] = toCanvas(meta._center.x, meta._center.y);
              // 执行绘制
              ctx.fillText(name, tx, ty);
            }
          }
        });
      }

      // 设施标记绘制逻辑
      const facilities = (map.raw.facilities || []).filter(f => f.geometry && (f.geometry.type === 'Point' || f.geometry.type === 'MultiPoint'))
      ctx.setFillStyle('rgba(255,120,40,0.95)')
      facilities.forEach(f => {
        try {
          const coords = f.geometry.type === 'Point' ? f.geometry.coordinates : (f.geometry.coordinates && f.geometry.coordinates[0])
          if (!coords) return
          const [cx, cy] = toCanvas(coords[0], coords[1])
          const rMark = Math.max(1, Math.min(4, Math.round(2 * s)))
          ctx.beginPath(); ctx.arc(cx, cy, rMark, 0, Math.PI * 2); ctx.fill()
          // 绘制白色中心
          ctx.setFillStyle('#fff')
          ctx.beginPath(); ctx.arc(cx, cy, Math.max(1, Math.round(rMark/2)), 0, Math.PI * 2); ctx.fill()
          ctx.setFillStyle('rgba(255,120,40,0.95)')
        } catch (e) {}
      })
      
      // --- 4. 关键：绘制 search 跳转过来的高亮区域 ---
      if (this.data.targetHighlightRings) {
        // 设置亮色边框样式：亮红色
        ctx.setStrokeStyle('#FF0000'); 
        ctx.setLineWidth(Math.max(3, 2 * s)); // 线宽随缩放变化，保持醒目
        ctx.setLineJoin('round');
        // 增加半透明填充，让区域中间也亮起来
        ctx.setFillStyle('rgba(255, 0, 0, 0.25)');
        this.data.targetHighlightRings.forEach(ring => {
          ctx.beginPath();
          ring.forEach((pt, i) => {
            const [cx, cy] = toCanvas(pt[0], pt[1]);
            if (i === 0) ctx.moveTo(cx, cy); else ctx.lineTo(cx, cy);
          });
          ctx.closePath();
          ctx.fill();   // 先填色
          ctx.stroke(); // 再描边
        });
      }

      // 绘制导航路径
      if (this.data.routePoints && this.data.routePoints.length > 0) {
        ctx.setStrokeStyle('#000'); // 路径颜色
        ctx.setLineWidth(4);          // 路径宽度
        ctx.setLineJoin('round');     // 折点圆润
        ctx.setLineCap('round');      // 线端圆润
        
        ctx.beginPath();
        this.data.routePoints.forEach((pt, i) => {
          const [cx, cy] = toCanvas(pt[0], pt[1]);
          if (i === 0) {
            ctx.moveTo(cx, cy);
          } else {
            ctx.lineTo(cx, cy);
          }
        });
        ctx.stroke();
      }

      // 绘制起终点标记
      if (this.data.startPoint) {
        const [cx, cy] = toCanvas(this.data.startPoint.x, this.data.startPoint.y)
        ctx.setFillStyle('#1AAD19') // 起点绿色
        ctx.beginPath(); ctx.arc(cx, cy, 4, 0, Math.PI * 2); ctx.fill()
        ctx.setStrokeStyle('#fff'); ctx.setLineWidth(2); ctx.stroke()
      }
      if (this.data.endPoint) {
        const [cx, cy] = toCanvas(this.data.endPoint.x, this.data.endPoint.y)
        ctx.setFillStyle('#e51c23') // 终点红色
        ctx.beginPath(); ctx.arc(cx, cy, 4, 0, Math.PI * 2); ctx.fill()
        ctx.setStrokeStyle('#fff'); ctx.setLineWidth(2); ctx.stroke()
      }

      this._drawn = { polygons, regions, minX, minY, mapW, mapH, baseScale, facilities }
      ctx.draw()
    }).exec()
  },

  // 核心交互
  onCanvasTap(e) {
    const clientX = (e.changedTouches && e.changedTouches[0] && e.changedTouches[0].clientX) || e.detail.x
    const clientY = (e.changedTouches && e.changedTouches[0] && e.changedTouches[0].clientY) || e.detail.y
    if (!this._drawn) return

    const query = wx.createSelectorQuery().in(this)
    query.select('.map-canvas').boundingClientRect(rect => {
      if (!rect) return
      const relX = clientX - rect.left, relY = clientY - rect.top
      const d = this._drawn
      const sVal = d.baseScale * this.data.scale
      const padX = (rect.width - d.mapW * sVal)/2
      const padY = (rect.height - d.mapH * sVal)/2

      const gx = (relX - this.data.offsetX - padX)/sVal + d.minX
      const gy = (relY - this.data.offsetY - padY)/sVal + d.minY
      // 如果处于起终点选择模式
      if (this.data.selectionMode) {
        if (this._isValidWalkable(gx, gy)) {
          if (this.data.selectionMode === 'start') {
            this.setData({ startPoint: { x: gx, y: gy } })
          } else {
            this.setData({ endPoint: { x: gx, y: gy } })
          }
          this.drawMap()
        } else {
          wx.showToast({ title: '此处无法通行', icon: 'none' })
        }
        return // 拦截弹窗逻辑
      }

      // 判定 1：设施点判定 12px 距离
      let hit = null
      if (d.facilities && d.facilities.length) {
        for (let i=0; i<d.facilities.length; i++) {
          const f = d.facilities[i]
          try {
            const coords = f.geometry.type === 'Point' ? f.geometry.coordinates : f.geometry.coordinates[0]
            const fx = (coords[0] - d.minX) * sVal + this.data.offsetX + padX
            const fy = (coords[1] - d.minY) * sVal + this.data.offsetY + padY
            if (Math.hypot(relX - fx, relY - fy) <= 12) {
              hit = { meta: f, type: 'facility' }; break
            }
          } catch(e){}
        }
      }

      // 判定 2：区域多边形判定
      if (!hit) {
        // const gx = (relX - this.data.offsetX - padX)/sVal + d.minX
        // const gy = (relY - this.data.offsetY - padY)/sVal + d.minY
        hit = d.regions.find(r => this._pointInPoly([gx, gy], r.coords[0]))
      }

      if (hit) {
        let meta = hit.meta || (hit.type === 'facility' ? hit.meta : null)
        if (hit.kind) meta = Object.assign({}, meta, { __kind: hit.kind })
        this.setData({ showRegionModal: true, activeRegion: this._normalizeRegionForModal(meta) })
      }
    }).exec()
  },

  _pointInPoly(pt, ring) {
    const x = pt[0], y = pt[1]; let inside = false
    for (let i=0, j=ring.length-1; i<ring.length; j=i++) {
      const xi = ring[i][0], yi = ring[i][1], xj = ring[j][0], yj = ring[j][1]
      if (((yi>y)!=(yj>y)) && (x < (xj-xi)*(y-yi)/(yj-yi)+xi)) inside = !inside
    }
    return inside
  },

  _normalizeRegionForModal(raw) {
    // 数据清洗
    if (!raw || typeof raw !== 'object') return raw
    const out = Object.assign({}, raw)
    out.is_facility = !!(raw.geometry && (raw.geometry.type === 'Point' || raw.geometry.type === 'MultiPoint'))
    out.is_shop = !!(raw.store_name || raw.__kind === 'storearea')
    out.is_event = !!(raw.__kind === 'eventarea')
    out.facility_type = raw.facility_type || raw.type || '公共设施'
    return out
  },

  // 缩放/拖拽逻辑
  onTouchStart(e) {
    const touches = e.touches || []
    if (touches.length >= 2) {
      const r = this._canvasRect; const p1 = touches[0]; const p2 = touches[1]
      const distance = Math.hypot(p2.clientX - p1.clientX, p2.clientY - p1.clientY)
      const d = this._drawn
      if (d) {
        const s = d.baseScale * this.data.scale
        const geoX = ((p1.clientX + p2.clientX)/2 - r.left - this.data.offsetX - (r.width - d.mapW * s)/2)/s + d.minX
        const geoY = ((p1.clientY + p2.clientY)/2 - r.top - this.data.offsetY - (r.height - d.mapH * s)/2)/s + d.minY
        this._pinchStart = { distance, baseScaleValue: this.data.scale, geoCenter: { x: geoX, y: geoY } }
      }
    } else if (touches.length === 1) {
      const t = touches[0]
      this._touchStart = { x: t.clientX, y: t.clientY, startOffsetX: this.data.offsetX, startOffsetY: this.data.offsetY }
    }
  },
  onTouchMove(e) {
    const touches = e.touches || []
    if (touches.length >= 2 && this._pinchStart && this._drawn) {
      const r = this._canvasRect; const p1 = touches[0]; const p2 = touches[1]
      const distance = Math.hypot(p2.clientX - p1.clientX, p2.clientY - p1.clientY)
      let newScale = Math.max(0.2, Math.min(this._pinchStart.baseScaleValue * (distance / this._pinchStart.distance), 6))
      const d = this._drawn; const sPrime = d.baseScale * newScale
      const geo = this._pinchStart.geoCenter
      const offsetX = (p1.clientX + p2.clientX)/2 - r.left - (geo.x - d.minX) * sPrime - (r.width - d.mapW * sPrime)/2
      const offsetY = (p1.clientY + p2.clientY)/2 - r.top - (geo.y - d.minY) * sPrime - (r.height - d.mapH * sPrime)/2
      this.setData({ scale: newScale, offsetX, offsetY }, () => { this.drawMap(); this._showZoomPercent() })
      return
    }
    const t = touches[0]
    if (!t || !this._touchStart) return
    this.setData({ offsetX: this._touchStart.startOffsetX + (t.clientX - this._touchStart.x), offsetY: this._touchStart.startOffsetY + (t.clientY - this._touchStart.y) }, () => this.drawMap())
  },
  onTouchEnd() { this._touchStart = null; this._pinchStart = null },
  zoomIn() { this.setData({ scale: Math.min(this.data.scale * 1.2, 6) }, () => { this.drawMap(); this._showZoomPercent() }) },
  zoomOut() { this.setData({ scale: Math.max(this.data.scale / 1.2, 0.2) }, () => { this.drawMap(); this._showZoomPercent() }) },
  _showZoomPercent() {
    if (this._zoomTimer) clearTimeout(this._zoomTimer)
    this.setData({ showZoomPercent: true, zoomPercent: Math.round(this.data.scale * 100) })
    this._zoomTimer = setTimeout(() => this.setData({ showZoomPercent: false }), 800)
  },
  closeRegionModal() { this.setData({ showRegionModal: false, activeRegion: null }) }
})