const util = require('../../utils/util')

const FACILITY_TYPE_MAP = {
  0: '电动扶梯',
  1: '灭火器',
  2: '安全出口',
  3: '服务台',
  4: '其他',
}

const FACILITY_ICON_MAP = {
  0: '/images/facility/escalator.png',
  1: '/images/facility/fire_extinguisher.png',
  2: '/images/facility/exit.png',
  3: '/images/facility/info.png',
  4: '/images/facility/other.png',
}

const FACILITY_ICON_BASE_COLOR = {
  0: 'rgba(24,144,255,0.95)',   // 蓝
  1: 'rgba(220,38,38,0.95)',    // 红
  2: 'rgba(34,197,94,0.95)',    // 绿
  3: 'rgba(245,158,11,0.95)',   // 黄
  4: 'rgba(255,120,40,0.95)',   // 橙
}

const EVENT_AREA_TYPE_MAP = {
  0: '其他活动',
  1: '促销活动',
  2: '展览活动',
  3: '表演活动',
}

const OTHER_AREA_TYPE_MAP = {
  0: '公共区域',
  1: '🚻卫生间',
  2: '🛗电梯间',
  3: '其他',
}

// 区域大类（eventarea/storearea/otherarea...）
const AREA_TYPE_MAP = {
  eventarea: '活动区域',
  storearea: '商铺区域',
  otherarea: '其他区域',
  publicarea: '公共区域'
}

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
      let targetIdx = 0;
      if (this._pendingMapId) {
        const idx = maps.findIndex(m => m.id == this._pendingMapId);
        if (idx !== -1) {
          targetIdx = idx;
        }
        this._pendingMapId = null; // 处理完即销毁
      }

      this.setData({ 
        maps,
        selectedMapIndex: targetIdx 
      }, () => {
        // 在 setData 的回调中执行加载详情，确保顺序
        if (maps.length) {
          this.loadMapDetail(targetIdx);
        }
      });
    }).catch(err => console.error('加载地图列表失败', err))
  },

  centroidOfRing(ring) {
    if (!Array.isArray(ring) || ring.length < 3) return null
    let area = 0
    let cxSum = 0
    let cySum = 0
    for (let i = 0; i < ring.length - 1; i++) {
      const x0 = ring[i][0], y0 = ring[i][1]
      const x1 = ring[i + 1][0], y1 = ring[i + 1][1]
      const a = x0 * y1 - x1 * y0
      area += a
      cxSum += (x0 + x1) * a
      cySum += (y0 + y1) * a
    }
    if (Math.abs(area) < 1e-9) {
      let sx = 0, sy = 0
      ring.forEach(p => { sx += p[0]; sy += p[1] })
      return [sx / ring.length, sy / ring.length]
    }
    area *= 0.5
    return [cxSum / (6 * area), cySum / (6 * area)]
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
    // 调用接口
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

      // === 严格抄自 home/index.js 的辅助函数 ===
      const showLabels = (this.data.scale || 1) >= 2.4
      const truncate = (text, maxChars) => {
        if (!text) return ''
        const s = String(text); if (s.length <= maxChars) return s
        return s.slice(0, Math.max(0, maxChars - 1)) + '…'
      }
      const drawLabel = (x, y, text, fontSize) => {
        if (!text) return
        const t = truncate(text, 10)
        ctx.setFontSize(fontSize); ctx.setTextAlign('center'); ctx.setTextBaseline('middle')
        ctx.setStrokeStyle('rgba(255,255,255,0.95)'); ctx.setLineWidth(3)
        ctx.strokeText(t, x, y)
        ctx.setFillStyle('#111'); ctx.fillText(t, x, y)
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
          ctx.closePath()
        })
        // 当一个路径包含多个闭合子路径时，Canvas 使用非零环绕原则实现镂空
        ctx.fill()
        ctx.stroke()
      })

      // 绘制区域
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

      if (showLabels) {
        regions.forEach(r => {
          try {
            const ring = r.coords && r.coords[0]
            const c = this.centroidOfRing(ring)
            if (!c) return
            const [lx, ly] = toCanvas(c[0], c[1])

            const metaWithKind = (r && r.meta && typeof r.meta === 'object')
              ? Object.assign({}, r.meta, { __kind: r.kind })
              : r.meta
            const norm = this._normalizeRegionForModal(metaWithKind)
            let label = ''
            if (r.kind === 'storearea') {
              label = (norm && (norm.store_name || norm.name)) || (r.meta && (r.meta.store_name || r.meta.name || r.meta.title))
            } else {
              label = (norm && norm.type_display) || (r.kind === 'eventarea' ? '活动区域' : '其他区域')
            }
            drawLabel(lx, ly, label, 12)
          } catch (e) {}
        })
      }

      // 绘制设施图片
      const facilities = (map.raw.facilities || []).filter(f => f.geometry && (f.geometry.type === 'Point' || f.geometry.type === 'MultiPoint'))
      facilities.forEach(f => {
        try {
          const coords = f.geometry.type === 'Point' ? f.geometry.coordinates : (f.geometry.coordinates && f.geometry.coordinates[0])
          if (!coords) return
          const [cx, cy] = toCanvas(coords[0], coords[1])
          
          const norm = this._normalizeRegionForModal(f)
          const code = (norm && (norm.type_code ?? norm.facility_type ?? norm.type))
          const num = Number(code)
          const key = (!Number.isNaN(num) && Number.isFinite(num)) ? num : String(code)
          
          const icon = FACILITY_ICON_MAP[key]
          const baseColor = FACILITY_ICON_BASE_COLOR[key] || 'rgba(255,120,40,0.95)'
          const iconSize = Math.max(10, Math.min(22, Math.round(10 * this.data.scale)))

          if (icon) {
            if (typeof ctx.setShadow === 'function') ctx.setShadow(0, 3, 8, 'rgba(0,0,0,0.22)')
            ctx.setFillStyle(baseColor)
            ctx.beginPath(); ctx.arc(cx, cy, (iconSize / 2) + 1, 0, Math.PI * 2); ctx.fill()
            if (typeof ctx.setShadow === 'function') ctx.setShadow(0, 0, 0, 'rgba(0,0,0,0)')
            ctx.drawImage(icon, cx - iconSize / 2, cy - iconSize / 2, iconSize, iconSize)
          } else {
            // 回退到圆点标记
            ctx.setFillStyle('rgba(255,120,40,0.95)')
            const rMark = Math.max(1, Math.min(4, Math.round(2 * s)))
            ctx.beginPath(); ctx.arc(cx, cy, rMark, 0, Math.PI * 2); ctx.fill()
          }

          if (showLabels) {
            const label = (norm && (FACILITY_TYPE_MAP[key] || `设施${key}`))
            if (label) {
              ctx.setFontSize(11); ctx.setFillStyle('#111'); ctx.setTextAlign('center')
              ctx.fillText(label, cx, cy - 18)
            }
          }
        } catch (e) { console.error('设施绘制异常', e) }
      })
      
      // 绘制 search 跳转过来的高亮区域
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
    const clientX = (e.changedTouches && e.changedTouches[0] && e.changedTouches[0].clientX) || (e.touches && e.touches[0] && e.touches[0].clientX) || e.detail.x
    const clientY = (e.changedTouches && e.changedTouches[0] && e.changedTouches[0].clientY) || (e.touches && e.touches[0] && e.touches[0].clientY) || e.detail.y
    if (!this._drawn) return

    const query = wx.createSelectorQuery().in(this)
    query.select('.map-canvas').boundingClientRect(rect => {
      if (!rect) return
      const relX = clientX - rect.left
      const relY = clientY - rect.top

      const d = this._drawn
      const sVal = d.baseScale * this.data.scale
      const padX = (rect.width - d.mapW * sVal) / 2
      const padY = (rect.height - d.mapH * sVal) / 2

      const gx = (relX - this.data.offsetX - padX) / sVal + d.minX
      const gy = (relY - this.data.offsetY - padY) / sVal + d.minY

      // 如果处于起终点选择模式，优先处理导航选点
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
        return 
      }

      // 1. 设施点判定 (12px 距离内优先命中)
      let hit = null
      if (d.facilities && d.facilities.length) {
        for (let i = 0; i < d.facilities.length; i++) {
          const f = d.facilities[i]
          try {
            const coords = f.geometry.type === 'Point' ? f.geometry.coordinates : (f.geometry.coordinates && f.geometry.coordinates[0])
            if (!coords) continue
            const fx = (coords[0] - d.minX) * sVal + this.data.offsetX + padX
            const fy = (coords[1] - d.minY) * sVal + this.data.offsetY + padY
            const dist = Math.hypot(relX - fx, relY - fy)
            if (dist <= 12) { hit = { meta: f, type: 'facility' }; break }
          } catch (e) {}
        }
      }

      // 2. 区域多边形判定
      if (!hit) {
        hit = d.regions.find(r => {
          const ring = r.coords && r.coords[0]
          return ring && this._pointInPoly([gx, gy], ring)
        })
      }

      if (hit) {
        let meta = hit.meta || (hit.type === 'facility' ? hit.meta : null)
        if (hit.kind && meta && typeof meta === 'object') {
          meta = Object.assign({}, meta, { __kind: hit.kind })
        }
        
        const norm = this._normalizeRegionForModal(meta)
        this.setData({ showRegionModal: true, activeRegion: norm })

        // 3. 异步补全详情 (补齐负责人、联系方式等，并确保分类不被冲掉)
        try {
          const areaId = (norm && norm._raw && (norm._raw.id || norm._raw.pk)) || (norm && (norm.id || norm.pk))
          // 设施弹窗不需要额外请求详情
          if (areaId && !norm.is_facility && !norm.organizer_name) {
            const tryPaths = []
            if (norm.is_event) {
              tryPaths.push(`/search/eventarea/${areaId}/`)
            } else if (norm.is_shop) {
              tryPaths.push(`/search/storearea/${areaId}/`)
            } else {
              tryPaths.push(`/search/otherarea/${areaId}/`)
            }

            const tryFetch = (i) => {
              if (i >= tryPaths.length) return Promise.reject(new Error('no search endpoint succeeded'))
              return util.apiRequest(tryPaths[i]).then(detail => detail).catch(() => tryFetch(i + 1))
            }

            tryFetch(0).then(detail => {
              const more = this._normalizeRegionForModal(detail)
              const merged = Object.assign({}, norm, more)
              // 关键：强制保留原始识别出的类型标志位，防止返回数据没有 kind 导致分类降级
              merged.is_facility = !!(norm.is_facility || more.is_facility)
              merged.is_shop = !!(norm.is_shop || more.is_shop)
              merged.is_event = !!(norm.is_event || more.is_event)
              const mergedRaw = Object.assign({}, (norm && norm._raw) ? norm._raw : {}, (more && more._raw) ? more._raw : {})
              if (norm && norm._raw && norm._raw.__kind && !mergedRaw.__kind) mergedRaw.__kind = norm._raw.__kind
              merged._raw = mergedRaw
              // 重新计算显示名称
              merged.type_display = this._getRegionTypeDisplay(merged)
              this.setData({ activeRegion: merged })
            }).catch(err => console.warn('Navigation fetch area detail failed', err))
          }
        } catch (e) { console.warn('Area detail fetch prepare failed', e) }
      }
    }).exec()
  },

  _getRegionTypeDisplay(out) {
    if (!out || typeof out !== 'object') return ''

    // 1. 设施
    if (out.is_facility) {
      const code = out.type_code ?? out.type
      const num = Number(code)
      const key = (!Number.isNaN(num) && Number.isFinite(num)) ? num : String(code)
      return FACILITY_TYPE_MAP[key] || '设施'
    }

    // 获取大类标识
    const kind = (out._raw && out._raw.__kind) ? out._raw.__kind : undefined
    
    // 2. 活动区域：显示“活动类型”映射（例如 1 -> 促销活动）
    if (out.is_event || kind === 'eventarea') {
      const code = out.type_code ?? out.type
      const num = Number(code)
      const key = (!Number.isNaN(num) && Number.isFinite(num)) ? num : String(code)
      return EVENT_AREA_TYPE_MAP[key] || '活动区域'
    }

    // 3. 商铺区域
    if (out.is_shop || kind === 'storearea') {
      return '商铺区域'
    }

    // 4. 其他区域：显示“其他区域类型”映射
    const code = out.type_code ?? out.type
    if (code !== undefined && code !== null && code !== '') {
      const num = Number(code)
      const key = (!Number.isNaN(num) && Number.isFinite(num)) ? num : String(code)
      const mapped = OTHER_AREA_TYPE_MAP[key]
      if (mapped) return mapped
    }

    return '其他区域'
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
    if (!raw || typeof raw !== 'object') return raw
    const src = raw.properties || raw.attributes || raw.store || raw
    
    // 辅助提取函数
    const pick = (keys) => {
      for (let k of keys) {
        if (raw[k] !== undefined) return raw[k]
        if (src && src[k] !== undefined) return src[k]
      }
      return undefined
    }

    const out = {}
    out.id = raw.id || raw.pk || src.id || src.pk
    out.store_name = pick(['store_name', 'shop_name', 'name', 'title'])
    out.name = out.store_name || pick(['name', 'title'])
    out.phone = pick(['phone', 'phone_number', 'contact_phone', 'tel'])
    out.open_time = pick(['open_time', 'open', 'business_hours'])
    out.close_time = pick(['close_time', 'close'])
    out.description = pick(['description', 'desc', 'detail', 'summary'])
    out.type = pick(['type', 'facility_type', 'category'])
    out.type_code = pick(['type_code', 'type_id', 'event_type_code', 'otherarea_type', 'category_code'])
    
    // 负责人与联系方式
    out.organizer_name = pick(['organizer_name', 'organizer', 'owner_name', 'owner', 'manager', 'contact_person'])
    out.organizer_phone = pick(['organizer_phone', 'organizer_tel', 'owner_phone', 'owner_tel', 'phone', 'contact_phone'])
    out.contact_person = out.organizer_name // 兼容旧版WXML
    out.owner_name = out.organizer_name     // 兼容旧版WXML
    out.owner_phone = out.organizer_phone   // 兼容旧版WXML

    // 分类判定逻辑
    const kind = raw.__kind || (src && src.__kind)
    const rawGeoType = raw && raw.geometry && raw.geometry.type
    const srcGeoType = src && src.geometry && src.geometry.type

    // 设施判定：地理坐标为点
    out.is_facility = (rawGeoType === 'Point' || rawGeoType === 'MultiPoint' || srcGeoType === 'Point' || srcGeoType === 'MultiPoint')
    
    // 活动判定：kind匹配、显式标志位、或类型名称包含关键字
    const typeLooksLikeEvent = (out.type && /event|activity|eventarea/i.test(String(out.type)))
    const explicitEvent = raw.event_id || pick(['is_event', 'event', 'activity'])
    out.is_event = !!(kind === 'eventarea' || explicitEvent || typeLooksLikeEvent || raw.is_event)

    // 商铺判定
    out.is_shop = !!((kind === 'storearea' || out.store_name || out.type === 'store') && !out.is_event && !out.is_facility)
    
    out.is_public = !!pick(['is_public', 'public'])
    out._raw = raw
    out.type_display = this._getRegionTypeDisplay(out)
    
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
  closeRegionModal() { this.setData({ showRegionModal: false, activeRegion: null }) },
  noop() {}
})