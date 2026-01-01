/*
 * Test Data Generated from 平面图.jpeg
 * Target: PostgreSQL / PostGIS
 * SRID: 2385
 */

BEGIN;

TRUNCATE TABLE 
    "admin",
    "event_storearea", "event_eventarea", "eventarea_map", "storearea_map", "facility_map", "otherarea_map",
    "event", "storearea", "eventarea", "facility", "otherarea", "map", "building"
RESTART IDENTITY CASCADE;

-- Admin (unchanged)
INSERT INTO "admin" (account, password, name) VALUES 
('admin', 'pbkdf2_sha256$260000$12345salt$jKqW1/8dK+XX+XX+XX+XX+XX+XX+XX+XX+XX+XX=', 'Super Admin'),
('manager', 'pbkdf2_sha256$260000$12345salt$jKqW1/8dK+XX+XX+XX+XX+XX+XX+XX+XX+XX+XX=', 'Store Manager');

DO $$
DECLARE
    v_building_id BIGINT;
    v_map_id BIGINT;
    v_map_id_floor1 BIGINT;
    v_id BIGINT;
    v_event_id BIGINT;
    v_floor INT;
BEGIN
    INSERT INTO "building" (name, address, description)
    VALUES ('Benchmark Mega Mall', '101 Tech Road, Taipei', 'A large shopping center for performance testing.')
    RETURNING id INTO v_building_id;

    -- Generate 4 floors with identical layout (same shapes/points)
    FOR v_floor IN 1..4 LOOP
        INSERT INTO "map" (building_id, floor_number, detail)
        VALUES (
            v_building_id,
            v_floor,
            ST_GeomFromText('GEOMETRYCOLLECTION(POLYGON((21.572 143.914, 19.106 128.814, 9.861 127.889, 3.698 105.393, 0.0 105.085, 0.0 80.74, 56.086 80.431, 56.086 66.564, 49.923 66.256, 49.923 61.017, 46.841 60.709, 46.841 47.458, 40.678 46.533, 40.678 12.327, 61.941 10.478, 62.866 14.176, 78.582 12.327, 91.834 17.874, 130.354 13.559, 131.279 33.898, 158.089 34.515, 159.014 40.062, 169.8 40.062, 175.039 34.206, 175.039 27.735, 147.92 23.112, 147.612 20.647, 144.222 20.647, 143.606 9.861, 163.636 8.012, 165.794 4.931, 189.831 0.0, 200.0 0.616, 200.0 52.08, 196.61 52.08, 192.604 57.319, 192.604 71.803, 200.0 72.111, 200.0 97.689, 195.069 97.997, 195.069 114.946, 190.139 115.254, 190.755 133.436, 200.0 134.361, 200.0 143.914, 189.214 146.379, 183.359 142.681, 176.888 142.681, 169.183 151.926, 31.433 151.926, 21.572 143.914)))', 2385)
        ) RETURNING id INTO v_map_id;

        IF v_floor = 1 THEN
            v_map_id_floor1 := v_map_id;
        END IF;

        -- Storeareas extracted from image
    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 001 URBAN STYLE 旗舰店',
        'F' || v_floor || '-Owner 001 陈美玲',
        '0912-345-678',
        'https://yauycf.top/root/images/store/UR.png',
        '10:00:00', '22:00:00',
        2,
        NULL,
        TRUE,
        '国际设计师品牌集合店，主打简约时尚与街头文化融合。每月第一周举行设计师见面会。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((158.089 17.565, 158.706 16.949, 158.706 13.559, 158.089 13.251, 157.473 8.629, 144.838 9.861, 144.222 10.478, 144.222 13.251, 144.838 13.559, 145.455 19.414, 158.089 17.565))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 002 Apple Store Taipei 101',
        'F' || v_floor || '-Owner 002 张致远',
        '0918-888-999',
        'https://yauycf.top/root/images/store/apple.png',
        '10:00:00', '22:00:00',
        3,
        NULL,
        TRUE,
        '苹果直营店，提供最新产品体验、Today at Apple工作坊、Genius Bar技术支持服务。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((125.424 22.496, 124.809 14.2, 100.245 16.952, 96.148 22.804, 95.532 26.81, 125.424 22.496))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 003 星巴克 Reserve Bar',
        'F' || v_floor || '-Owner 003 林雅婷',
        '0920-555-666',
        'https://yauycf.top/root/images/store/starbucks.png',
        '07:00:00', '23:00:00',
        1,
        NULL,
        TRUE,
        '星巴克臻选店，提供稀有咖啡豆手冲服务，每月举办咖啡品鉴会，设有露天座位区。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((75.809 12.943, 77.042 27.427, 88.444 25.578, 88.444 22.804, 89.676 22.496, 89.676 20.955, 90.909 19.414, 90.442 17.313, 87.412 16.045, 81.356 14.792, 78.582 12.943, 75.809 12.943))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 004 Sephora 亚洲旗舰店',
        'F' || v_floor || '-Owner 004 王诗涵',
        '0933-777-888',
        'https://yauycf.top/root/images/store/sephora.png',
        '11:00:00', '22:00:00',
        4,
        NULL,
        TRUE,
        '美妆概念店，提供AR试妆、专业彩妆咨询、个性化护肤方案，设有美妆教学区。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((59.168 26.502, 59.168 27.427, 60.401 27.735, 60.401 28.659, 65.023 28.659, 65.331 28.043, 68.721 28.043, 69.337 27.427, 68.721 19.723, 57.319 20.339, 56.703 20.955, 56.703 22.496, 59.168 26.502))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 005 Kidzania 儿童职业体验城',
        'F' || v_floor || '-Owner 005 黄志明',
        '0910-123-456',
        'https://yauycf.top/root/images/store/KidZania.png',
        '09:30:00', '20:30:00',
        3,
        NULL,
        TRUE,
        '专为3-14岁儿童设计的职业体验乐园，设有消防局、电视台、银行等20+职业模拟场景。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((114.33 29.584, 105.393 30.2, 105.085 32.049, 99.846 30.817, 92.45 32.049, 90.601 35.747, 90.601 39.753, 102.619 39.137, 102.928 37.288, 105.701 37.288, 107.242 38.213, 107.242 40.986, 114.33 40.37, 114.33 29.584))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 006 诚品生活 Eslite Spectrum',
        'F' || v_floor || '-Owner 006 吴嘉豪',
        '0922-333-444',
        'https://yauycf.top/root/images/store/eslite.png',
        '10:00:00', '24:00:00',
        0,
        NULL,
        TRUE,
        '24小时营业的文化复合空间，包含书店、文创商品、咖啡厅、展览空间和讲座区。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((153.159 42.219, 154.391 35.131, 133.128 34.515, 131.279 35.131, 131.279 42.219, 153.159 42.219))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 007 World Gym 科技旗舰店',
        'F' || v_floor || '-Owner 007 刘建华',
        '0935-678-901',
        'https://yauycf.top/root/images/store/world gym.png',
        '06:00:00', '24:00:00',
        4,
        NULL,
        TRUE,
        '配备智能健身设备、VR动感单车、专业拳击台、空中瑜伽教室及营养咨询中心。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((84.129 37.596, 83.513 33.282, 80.123 33.282, 80.123 58.86, 81.972 59.784, 81.972 61.941, 84.129 61.941, 84.129 37.596))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 008 鼎泰丰 小笼包专卖',
        'F' || v_floor || '-Owner 008 李正元',
        '0916-789-012',
        'https://yauycf.top/root/images/store/dingtaifeng.png',
        '11:00:00', '21:00:00',
        1,
        NULL,
        TRUE,
        '米其林一星餐厅美食广场分店，提供招牌小笼包、红油抄手、排骨炒饭等经典餐点。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((61.325 55.47, 50.847 32.666, 44.992 34.515, 44.376 45.3, 47.458 45.609, 47.458 59.476, 50.539 60.401, 50.539 65.639, 57.011 65.639, 57.319 70.57, 61.017 70.878, 61.633 75.501, 67.488 75.501, 61.325 55.47))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 009 Studio A 苹果授权经销商',
        'F' || v_floor || '-Owner 009 蔡文杰',
        '0925-456-789',
        'https://yauycf.top/root/images/store/studio_a.png',
        '11:00:00', '21:30:00',
        0,
        NULL,
        TRUE,
        '苹果授权维修中心，提供原厂配件、专业维修服务、企业采购咨询及教育优惠办理。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((172.265 75.501, 172.265 53.621, 168.567 52.08, 170.416 46.225, 167.951 44.684, 167.951 42.527, 157.781 42.527, 157.781 58.86, 150.385 69.646, 149.769 76.117, 172.265 75.501))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 010 Cartier 卡地亚精品店',
        'F' || v_floor || '-Owner 010 法国总部直营',
        '+33158181800',
        'https://yauycf.top/root/images/store/cartier.png',
        '11:00:00', '20:00:00',
        0,
        NULL,
        TRUE,
        '法国奢侈品牌卡地亚专门店，提供高级珠宝、腕表、皮具及婚礼系列，设有VIP贵宾室。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((155.008 92.142, 155.932 94.607, 157.473 94.607, 157.781 92.142, 165.485 92.758, 166.102 80.123, 146.687 80.123, 142.373 92.142, 155.008 92.142))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 011 NIKE Rise 概念店',
        'F' || v_floor || '-Owner 011 王健雄',
        '0930-111-222',
        'https://yauycf.top/root/images/store/NIKE rise.png',
        '09:00:00', '22:00:00',
        2,
        NULL,
        TRUE,
        '亚洲首家Nike Rise概念店，提供3D足部扫描定制鞋垫、AR虚拟试衣间、运动数据分析服务。设有篮球测试区与跑步机体验区。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((187.365 73.344, 187.365 80.431, 185.516 81.972, 185.516 86.595, 193.529 88.136, 193.529 97.072, 199.98 96.458, 199.98 73.344, 187.365 73.344))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 012 MUJI 家居生活馆',
        'F' || v_floor || '-Owner 012 李佳蓉',
        '0915-333-444',
        'https://yauycf.top/root/images/store/muji.png',
        '10:30:00', '22:00:00',
        3,
        NULL,
        TRUE,
        '包含家具展示间、食品贩卖区、服装定制服务、书籍区及Café&Meal MUJI餐厅。提供家具配置咨询服务。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((145.146 69.954, 145.763 52.388, 129.43 51.772, 127.581 78.582, 134.977 82.589, 134.669 89.985, 99.538 89.676, 91.525 68.721, 91.525 57.935, 100.154 57.011, 100.154 50.539, 88.752 49.307, 89.368 90.909, 115.871 100.154, 132.82 98.305, 145.146 69.954))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 013 松本清 Matsumoto Kiyoshi',
        'F' || v_floor || '-Owner 013 田中一郎',
        '0919-555-666',
        'https://yauycf.top/root/images/store/matsumoto_kiyoshi.png',
        '09:00:00', '22:00:00',
        4,
        NULL,
        TRUE,
        '日本知名药妆连锁店台湾首店，提供3000多种日本直送药品、化妆品、健康食品。设有免税柜台及日语咨询服务。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((37.288 114.946, 38.213 112.481, 46.225 108.783, 63.79 108.166, 66.872 106.317, 69.337 97.997, 72.419 97.689, 70.57 81.972, 64.715 81.972, 64.715 89.06, 59.784 89.985, 58.86 99.23, 41.294 97.997, 41.294 108.166, 34.515 114.33, 37.288 114.946))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 014 PETsMART 宠物百货',
        'F' || v_floor || '-Owner 014 陈爱宠',
        '0928-777-888',
        'https://yauycf.top/root/images/store/petsMART.png',
        '10:00:00', '21:30:00',
        5,
        NULL,
        TRUE,
        '宠物百货，提供宠物食品、玩具、服饰、美容服务、医疗咨询、宠物旅馆。设有宠物游泳池及训练场。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((74.884 119.569, 73.652 118.952, 57.319 120.801, 57.319 124.191, 57.935 124.807, 63.79 124.807, 65.331 126.04, 72.419 126.04, 72.727 127.889, 74.884 127.273, 74.884 119.569))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 015 Whole Foods Market 全食超市',
        'F' || v_floor || '-Owner 015 张健康',
        '0932-999-000',
        'https://yauycf.top/root/images/store/wholeFoodsMarket-logo.png',
        '08:00:00', '22:00:00',
        1,
        NULL,
        TRUE,
        '美国有机超市品牌亚洲首店，提供有机蔬果、无添加食品、公平贸易咖啡、现做沙拉吧、果汁吧及有机熟食。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((15.1 127.273, 16.025 123.575, 21.88 122.342, 23.421 119.26, 24.961 119.26, 24.345 114.022, 22.188 114.022, 13.251 109.707, 6.78 110.94, 7.396 116.179, 11.094 127.889, 15.1 127.273))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 016 B&O Play 听觉实验室',
        'F' || v_floor || '-Owner 016 林音悦',
        '0911-222-333',
        'https://yauycf.top/root/images/store/B&O Play.png',
        '11:00:00', '22:00:00',
        2,
        NULL,
        TRUE,
        '丹麦奢华音响品牌体验店，设有7间不同声学设计的试听室、私人影院体验区、音响定制咨询服务。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((197.535 134.977, 189.522 134.669, 189.522 125.732, 182.435 128.197, 180.894 120.185, 161.479 117.72, 161.171 107.242, 157.781 107.242, 157.473 104.16, 140.524 101.695, 151.618 121.726, 163.328 130.971, 189.831 145.763, 197.535 142.065, 197.535 134.977))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 017 Hands Craft Studio 手作实验室',
        'F' || v_floor || '-Owner 017 王艺师',
        '0920-444-555',
        'https://yauycf.top/root/images/store/Hands Craft.png',
        '11:00:00', '21:00:00',
        3,
        NULL,
        TRUE,
        '提供皮革制作、金工体验、陶艺创作、木工DIY等手作课程。材料齐全，专业导师指导，可制作个人专属作品。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((120.801 150.693, 169.183 150.693, 172.265 144.838, 157.165 139.291, 151.31 131.895, 149.461 139.291, 139.908 139.291, 139.599 133.128, 144.53 130.354, 144.53 126.348, 136.518 119.569, 134.977 124.807, 131.895 125.116, 129.738 119.569, 134.052 117.72, 119.569 115.871, 120.801 150.693))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 018 TWININGS 皇家茶廊',
        'F' || v_floor || '-Owner 018 英国总部直营',
        '+442073520000',
        'https://yauycf.top/root/images/store/TWININGS.png',
        '09:00:00', '22:00:00',
        4,
        NULL,
        TRUE,
        '英国300年历史茶品牌，提供超过100种茶叶选择、茶具贩卖、茶艺教学、英式下午茶体验服务。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((114.33 150.693, 114.33 142.989, 107.242 142.373, 104.468 140.216, 103.852 133.744, 100.154 133.436, 100.154 124.499, 115.562 124.191, 114.946 115.871, 80.74 118.336, 81.356 150.693, 114.33 150.693))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 019 VR ZONE 虚拟实境乐园',
        'F' || v_floor || '-Owner 019 陈科技',
        '0917-666-777',
        'https://yauycf.top/root/images/store/VR ZONE.png',
        '09:00:00', '22:00:00',
        5,
        NULL,
        TRUE,
        '亚洲最大VR体验中心，提供20+种VR游戏、恐怖体验、飞行模拟、赛车竞技。适合个人、情侣、团体体验。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((56.086 150.693, 71.803 150.693, 73.652 139.291, 55.47 139.291, 55.47 150.077, 56.086 150.693))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 020 海马体 HIMO 证件照专门店',
        'F' || v_floor || '-Owner 020 林摄影',
        '0925-888-999',
        'https://yauycf.top/root/images/store/haimaiti.png',
        '09:40:00', '22:40:00',
        1,
        NULL,
        TRUE,
        '专业证件照、形象照拍摄，提供化妆、造型、修图一站式服务。设有8种主题摄影棚，最快2小时取件。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((31.433 150.693, 50.847 150.693, 50.847 139.908, 39.445 139.291, 39.137 133.744, 50.231 132.82, 54.545 134.669, 53.929 122.034, 41.911 124.499, 31.741 130.663, 20.955 133.744, 23.421 144.53, 31.433 150.693))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    -- Otherareas extracted from image
    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        1, TRUE, TRUE,
        'Other Area 01 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((59.804 13.54, 59.804 19.394, 63.162 19.394, 63.47 18.778, 70.55 18.778, 70.55 14.196, 63.038 14.196, 62.836 14.22, 62.82 14.159, 61.921 13.259, 61.921 10.563, 61.91 10.521, 60.333 10.658, 60.104 11.114, 55.49 11.114, 55.49 13.232, 59.804 13.54))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        1, TRUE, TRUE,
        'Other Area 02 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((105.388 29.256, 109.387 29.256, 109.695 28.639, 115.546 28.639, 115.855 27.407, 124.171 27.407, 124.171 24.057, 119.572 24.057, 115.566 25.29, 107.255 25.905, 106.947 26.521, 98.017 27.138, 98.017 30.488, 103.231 30.488, 105.388 29.256))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        3, TRUE, TRUE,
        'Other Area 03 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((43.431 34.502, 48.07 32.337, 50.211 32.337, 50.211 30.204, 45.901 20.968, 42.212 17.894, 40.718 17.894, 40.718 40.862, 41.314 41.906, 41.314 46.513, 43.431 46.513, 43.431 34.502))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        0, TRUE, TRUE,
        'Other Area 04 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((148.553 48.091, 147.937 50.865, 146.091 51.173, 146.091 54.527, 148.556 54.836, 148.556 60.109, 146.707 60.418, 146.707 62.538, 155.234 62.538, 155.435 62.246, 155.604 61.999, 155.604 58.568, 154.371 58.259, 154.371 49.941, 151.906 49.633, 151.906 47.482, 148.553 48.091))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        0, TRUE, TRUE,
        'Other Area 05 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((192.564 57.305, 192.584 57.279, 192.584 56.696, 195.984 52.06, 196.575 52.06, 196.59 52.04, 199.96 52.04, 199.96 1.858, 195.685 0.637, 164.627 6.667, 164.178 7.308, 166.431 12.941, 164.584 21.866, 167.66 22.788, 168.276 26.177, 177.524 27.718, 177.524 31.75, 175.079 34.092, 175.079 34.221, 170.241 39.629, 172.197 53.571, 172.285 53.608, 172.285 54.198, 172.591 56.379, 179.372 58.537, 179.988 66.852, 192.564 66.852, 192.564 57.305))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        0, TRUE, TRUE,
        'Other Area 06 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((66.274 38.227, 56.729 41.923, 69.043 75.481, 82.877 75.481, 82.877 63.465, 84.726 63.157, 84.726 59.803, 84.149 59.771, 84.149 61.961, 81.952 61.961, 81.952 59.796, 81.62 59.631, 79.179 59.495, 79.179 33.306, 66.582 35.764, 66.274 38.227))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        0, TRUE, TRUE,
        'Other Area 07 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((134.032 83.225, 130.027 83.225, 129.874 79.847, 127.56 78.593, 127.722 76.244, 126.634 76.135, 130.949 29.604, 125.748 29.604, 122.974 41.313, 104.797 41.93, 104.797 46.549, 100.483 47.474, 101.1 57.646, 92.472 57.954, 93.956 75.021, 95.573 79.25, 99.865 79.488, 100.481 89.042, 106.685 89.719, 117.574 89.815, 117.703 89.04, 134.032 89.04, 134.032 83.225))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        0, TRUE, TRUE,
        'Other Area 08 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((32.069 113.077, 34.815 113.077, 40.35 108.157, 40.659 97.049, 55.758 98.898, 55.758 91.821, 59.749 90.132, 59.766 89.968, 60.432 89.843, 63.77 88.431, 63.77 79.525, 60.072 79.217, 60.072 71.515, 56.126 71.515, 56.126 80.471, 55.826 80.472, 55.797 81.376, 0.04 81.376, 0.04 101.373, 24.98 105.068, 25.289 109.995, 27.407 109.995, 27.407 98.594, 31.761 98.284, 32.069 113.077))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        0, TRUE, TRUE,
        'Other Area 09 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((190.119 124.792, 190.119 115.845, 190.119 115.837, 190.1 115.272, 185.188 114.965, 185.188 97.362, 192.584 97.053, 192.584 88.156, 184.881 88.156, 184.573 81.992, 177.487 81.992, 176.562 76.445, 173.209 76.445, 172.9 80.76, 167.046 80.76, 166.737 93.087, 157.714 92.846, 157.491 94.627, 155.918 94.627, 155.226 92.78, 143.626 92.471, 143.626 95.203, 157.492 95.203, 157.802 100.174, 140.544 100.482, 140.544 101.678, 146.879 102.599, 157.481 102.599, 161.499 106.618, 161.499 116.777, 182.145 119.242, 182.454 127.246, 190.119 124.792))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        2, TRUE, TRUE,
        'Other Area 10 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((148.824 132.5, 149.441 132.191, 149.441 129.45, 145.475 129.45, 145.475 130.979, 144.538 131.915, 143.622 131.915, 143.313 133.148, 140.544 133.148, 140.544 138.347, 148.824 138.347, 148.824 132.5))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        1, TRUE, TRUE,
        'Other Area 11 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((74.863 128.834, 72.094 128.834, 71.786 126.984, 57.3 125.75, 56.992 120.821, 54.875 120.821, 55.491 135.304, 50.522 135.614, 50.214 133.764, 40.082 133.764, 40.082 138.347, 74.249 138.347, 74.863 128.834))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        2, TRUE, TRUE,
        'Other Area 12 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((114.926 139.896, 115.542 139.587, 115.542 125.136, 101.099 125.136, 101.099 132.802, 104.797 133.11, 104.797 139.581, 107.262 139.89, 107.262 142.045, 114.926 142.045, 114.926 139.896))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    -- Eventareas extracted from image
    INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape)
    VALUES (
        '文化局', '02-2345-6789', 3, TRUE,
        '可容纳200人的剧场，配备专业舞台灯光、音响系统、遮阳棚及阶梯式观众席。适合举办音乐会、话剧、舞蹈表演。(Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((102.331 30.528, 102.331 31.381, 105.065 32.024, 105.065 30.22, 103.78 30.22, 103.241 30.528, 102.331 30.528))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "eventarea_map" (eventarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape)
    VALUES (
        '科学教育馆', '02-1122-3344', 1, TRUE,
        '互动科学实验区，配备物理实验装置、化学实验台、天文望远镜及机器人编程工作站。(Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((91.545 68.701, 92.122 68.701, 92.122 57.891, 91.545 57.953, 91.545 68.701))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "eventarea_map" (eventarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape)
    VALUES (
        '购物中心', '02-1234-5678', 1, TRUE,
        '通用活动区域。(Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((127.725 76.204, 127.793 75.213, 126.985 75.213, 126.985 76.13, 127.725 76.204))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "eventarea_map" (eventarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape)
    VALUES (
        '购物中心', '02-1234-5678', 2, TRUE,
        '长形走廊展示区，配备交互式触摸屏、VR体验站、智能家居模拟间及新品发布舞台。两侧设有品牌展示柜。(Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((166.698 76.445, 149.753 76.445, 149.445 75.213, 147.94 75.213, 147.94 79.795, 166.698 79.795, 166.698 76.445))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "eventarea_map" (eventarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape)
    VALUES (
        '美食节筹委会', '0928-888-999', 1, TRUE,
        '美食摊位区，设有20个标准摊位、公共用餐区。(Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((38.885 112.193, 38.229 112.496, 37.301 114.969, 34.473 114.341, 36.835 112.193, 35.87 112.193, 34.831 113.117, 32.686 113.117, 32.686 113.703, 35.138 115.542, 37.28 115.542, 39.117 113.705, 39.117 112.193, 38.885 112.193))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "eventarea_map" (eventarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape)
    VALUES (
        '创客协会', '02-3456-7890', 2, TRUE,
        '配备10个工作台，每台配备3D打印机、激光切割机、电子焊接设备，设有材料储存区及作品展示墙。(Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((134.649 120.784, 136.216 120.523, 136.498 119.566, 136.498 118.963, 134.663 117.74, 134.056 117.74, 130.066 119.45, 130.066 119.889, 129.914 119.966, 130.788 122.214, 131.915 122.636, 131.915 124.795, 132.413 125.044, 134.205 124.864, 134.649 124.82, 134.649 120.784))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "eventarea_map" (eventarea_id, map_id) VALUES (v_id, v_map_id);

    -- Facilities sampled from remaining pixels
    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        1, TRUE, 'Facility 01 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(140.216 118.644)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        2, TRUE, 'Facility 02 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(54.854 144.53)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        3, TRUE, 'Facility 03 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(71.186 112.481)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        4, TRUE, 'Facility 04 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(23.729 108.475)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        0, TRUE, 'Facility 05 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(181.202 79.815)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        1, TRUE, 'Facility 06 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(189.522 72.727)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        2, TRUE, 'Facility 07 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(93.374 20.955)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        3, TRUE, 'Facility 08 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(178.737 78.582)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        3, TRUE, 'Facility 09 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(73.344 29.276)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        0, TRUE, 'Facility 10 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(86.287 90.909)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        1, TRUE, 'Facility 11 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(150.385 99.846)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        2, TRUE, 'Facility 12 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(171.649 137.75)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        3, TRUE, 'Facility 13 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(87.827 60.709)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        0, TRUE, 'Facility 14 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(187.673 72.727)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        0, TRUE, 'Facility 15 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(76.117 88.752)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        1, TRUE, 'Facility 16 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(53.313 147.92)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        2, TRUE, 'Facility 17 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(85.67 113.405)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "facility" (type, is_active, description, location)
    VALUES (
        3, TRUE, 'Facility 18 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POINT(75.193 76.425)', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_id, v_map_id);

        -- end per-floor generation
    END LOOP;

    -- Events: only generate & associate with Floor 1 areas (explicitly listed for easy editing)

    INSERT INTO "event" (event_name, start_date, end_date, image_url, is_active, description)
    VALUES ('万圣节惊奇派对', NOW(), NOW() + INTERVAL '7 days', 'https://yauycf.top/root/images/event/halloween.png', TRUE, '万圣节主题狂欢派对，包含鬼屋探险、变装比赛、南瓜雕刻工作坊、不给糖就捣蛋路线。现场提供免费化妆服务、恐怖主题美食摊位。')
    RETURNING id INTO v_event_id;
    INSERT INTO "event_storearea" (event_id, storearea_id)
        SELECT v_event_id, s.id
        FROM "storearea" s
        JOIN "storearea_map" sm ON sm.storearea_id = s.id
        WHERE sm.map_id = v_map_id_floor1
            AND s.store_name IN ('F1-Store 004 Sephora 亚洲旗舰店', 'F1-Store 017 Hands Craft Studio 手作实验室', 'F1-Store 014 PETsMART 宠物百货');
    INSERT INTO "event_eventarea" (event_id, eventarea_id)
        SELECT v_event_id, e.id
        FROM "eventarea" e
        JOIN "eventarea_map" em ON em.eventarea_id = e.id
        WHERE em.map_id = v_map_id_floor1
            AND e.description = '长形走廊展示区，配备交互式触摸屏、VR体验站、智能家居模拟间及新品发布舞台。两侧设有品牌展示柜。(Generated, Floor 1)';

    INSERT INTO "event" (event_name, start_date, end_date, image_url, is_active, description)
    VALUES ('科技新品发布', NOW(), NOW() + INTERVAL '7 days', 'https://yauycf.top/root/images/event/tech_launch.png', TRUE, '深度融合"展示、销售、互动、体验"，打造沉浸式场景。')
    RETURNING id INTO v_event_id;
    INSERT INTO "event_storearea" (event_id, storearea_id)
        SELECT v_event_id, s.id
        FROM "storearea" s
        JOIN "storearea_map" sm ON sm.storearea_id = s.id
        WHERE sm.map_id = v_map_id_floor1
            AND s.store_name IN ('F1-Store 007 World Gym 科技旗舰店', 'F1-Store 002 Apple Store Taipei 101');
    INSERT INTO "event_eventarea" (event_id, eventarea_id)
        SELECT v_event_id, e.id
        FROM "eventarea" e
        JOIN "eventarea_map" em ON em.eventarea_id = e.id
        WHERE em.map_id = v_map_id_floor1
            AND e.description = '互动科学实验区，配备物理实验装置、化学实验台、天文望远镜及机器人编程工作站。(Generated, Floor 1)';

    INSERT INTO "event" (event_name, start_date, end_date, image_url, is_active, description)
    VALUES ('2024毛小孩时装周', NOW(), NOW() + INTERVAL '7 days', 'https://yauycf.top/root/images/event/pet_fashion.png', TRUE, '宠物时装走秀比赛，设有创意造型组、亲子配对组、最佳才艺组。现场提供宠物美容服务、摄影棚、领养服务摊位。冠军可获得宠物百货购物金1万元。')
    RETURNING id INTO v_event_id;
    INSERT INTO "event_storearea" (event_id, storearea_id)
        SELECT v_event_id, s.id
        FROM "storearea" s
        JOIN "storearea_map" sm ON sm.storearea_id = s.id
        WHERE sm.map_id = v_map_id_floor1
            AND s.store_name IN ('F1-Store 001 URBAN STYLE 旗舰店', 'F1-Store 014 PETsMART 宠物百货', 'F1-Store 020 海马体 HIMO 证件照专门店');
    INSERT INTO "event_eventarea" (event_id, eventarea_id)
        SELECT v_event_id, e.id
        FROM "eventarea" e
        JOIN "eventarea_map" em ON em.eventarea_id = e.id
        WHERE em.map_id = v_map_id_floor1
            AND e.description = '可容纳200人的剧场，配备专业舞台灯光、音响系统、遮阳棚及阶梯式观众席。适合举办音乐会、话剧、舞蹈表演。(Generated, Floor 1)';

    INSERT INTO "event" (event_name, start_date, end_date, image_url, is_active, description)
    VALUES ('有机生活节', NOW(), NOW() + INTERVAL '7 days', 'https://yauycf.top/root/images/event/organic_lifestyle.png', TRUE, '倡导环保永续生活方式，包含有机农产品展售、零废弃工作坊、环保手作体验、绿色饮食讲座。现场设有二手物交换站、环保杯租借服务。')
    RETURNING id INTO v_event_id;
    INSERT INTO "event_storearea" (event_id, storearea_id)
        SELECT v_event_id, s.id
        FROM "storearea" s
        JOIN "storearea_map" sm ON sm.storearea_id = s.id
        WHERE sm.map_id = v_map_id_floor1
            AND s.store_name IN ('F1-Store 003 星巴克 Reserve Bar', 'F1-Store 015 Whole Foods Market 全食超市', 'F1-Store 017 Hands Craft Studio 手作实验室');
    INSERT INTO "event_eventarea" (event_id, eventarea_id)
        SELECT v_event_id, e.id
        FROM "eventarea" e
        JOIN "eventarea_map" em ON em.eventarea_id = e.id
        WHERE em.map_id = v_map_id_floor1
            AND e.description = '长形走廊展示区，配备交互式触摸屏、VR体验站、智能家居模拟间及新品发布舞台。两侧设有品牌展示柜。(Generated, Floor 1)';

    INSERT INTO "event" (event_name, start_date, end_date, image_url, is_active, description)
    VALUES ('电竞狂欢节', NOW(), NOW() + INTERVAL '7 days', 'https://yauycf.top/root/images/event/esports.png', TRUE, '专业比赛舞台配备实时转播，现场提供电竞设备体验区、选手签名会。')
    RETURNING id INTO v_event_id;
    INSERT INTO "event_storearea" (event_id, storearea_id)
        SELECT v_event_id, s.id
        FROM "storearea" s
        JOIN "storearea_map" sm ON sm.storearea_id = s.id
        WHERE sm.map_id = v_map_id_floor1
            AND s.store_name IN ('F1-Store 002 Apple Store Taipei 101', 'F1-Store 009 Studio A 苹果授权经销商', 'F1-Store VR ZONE 虚拟实境乐园');
    INSERT INTO "event_eventarea" (event_id, eventarea_id)
        SELECT v_event_id, e.id
        FROM "eventarea" e
        JOIN "eventarea_map" em ON em.eventarea_id = e.id
        WHERE em.map_id = v_map_id_floor1
            AND e.description = '长形走廊展示区，配备交互式触摸屏、VR体验站、智能家居模拟间及新品发布舞台。两侧设有品牌展示柜。(Generated, Floor 1)';

    INSERT INTO "event" (event_name, start_date, end_date, image_url, is_active, description)
    VALUES ('冰品嘉年华', NOW(), NOW() + INTERVAL '7 days', 'https://yauycf.top/root/images/event/ice_carnival.png', TRUE, '汇聚20家特色冰品摊位，包含传统刨冰、创意冰淇淋、冻饮调酒。设有冰品造型比赛、大胃王挑战、DIY冰淇淋工作坊。')
    RETURNING id INTO v_event_id;
    INSERT INTO "event_storearea" (event_id, storearea_id)
        SELECT v_event_id, s.id
        FROM "storearea" s
        JOIN "storearea_map" sm ON sm.storearea_id = s.id
        WHERE sm.map_id = v_map_id_floor1
            AND s.store_name IN ('F1-Store 003 星巴克 Reserve Bar', 'F1-Store 008 鼎泰丰 小笼包专卖', 'F1-Store 018 TWININGS 皇家茶廊');
    INSERT INTO "event_eventarea" (event_id, eventarea_id)
        SELECT v_event_id, e.id
        FROM "eventarea" e
        JOIN "eventarea_map" em ON em.eventarea_id = e.id
        WHERE em.map_id = v_map_id_floor1
            AND e.description = '美食摊位区，设有20个标准摊位、公共用餐区。(Generated, Floor 1)';

    INSERT INTO "event" (event_name, start_date, end_date, image_url, is_active, description)
    VALUES ('小小科学家夏令营', NOW(), NOW() + INTERVAL '7 days', 'https://yauycf.top/root/images/event/kids_scientist.png', TRUE, '科学主题夏令营，每日不同主题：化学实验日、机器人编程日、天文观测日、生态探索日、科学成果展。适合7-12岁儿童参加。')
    RETURNING id INTO v_event_id;
    INSERT INTO "event_storearea" (event_id, storearea_id)
        SELECT v_event_id, s.id
        FROM "storearea" s
        JOIN "storearea_map" sm ON sm.storearea_id = s.id
        WHERE sm.map_id = v_map_id_floor1
            AND s.store_name IN ('F1-Store 019 VR ZONE 虚拟实境乐园', 'F1-Store 006 诚品生活 Eslite Spectrum', 'F1-Store 005 Kidzania 儿童职业体验城');
    INSERT INTO "event_eventarea" (event_id, eventarea_id)
        SELECT v_event_id, e.id
        FROM "eventarea" e
        JOIN "eventarea_map" em ON em.eventarea_id = e.id
        WHERE em.map_id = v_map_id_floor1
            AND e.description = '可容纳200人的剧场，配备专业舞台灯光、音响系统、遮阳棚及阶梯式观众席。适合举办音乐会、话剧、舞蹈表演。(Generated, Floor 1)';

    INSERT INTO "event" (event_name, start_date, end_date, image_url, is_active, description)
    VALUES ('时尚艺术周', NOW(), NOW() + INTERVAL '7 days', 'https://yauycf.top/root/images/event/fashion_art.png', TRUE, '结合时尚与艺术的跨界活动，包含新锐设计师时装秀、艺术装置展览、街头艺术创作、时尚摄影展。设有设计师对谈会及workshop。')
    RETURNING id INTO v_event_id;
    INSERT INTO "event_storearea" (event_id, storearea_id)
        SELECT v_event_id, s.id
        FROM "storearea" s
        JOIN "storearea_map" sm ON sm.storearea_id = s.id
        WHERE sm.map_id = v_map_id_floor1
            AND s.store_name IN ('F1-Store 001 URBAN STYLE 旗舰店', 'F1-Store 004 Sephora 亚洲旗舰店', 'F1-Store 010 Cartier 卡地亚精品店');
    INSERT INTO "event_eventarea" (event_id, eventarea_id)
        SELECT v_event_id, e.id
        FROM "eventarea" e
        JOIN "eventarea_map" em ON em.eventarea_id = e.id
        WHERE em.map_id = v_map_id_floor1
            AND e.description = '可容纳200人的剧场，配备专业舞台灯光、音响系统、遮阳棚及阶梯式观众席。适合举办音乐会、话剧、舞蹈表演。(Generated, Floor 1)';

    INSERT INTO "event" (event_name, start_date, end_date, image_url, is_active, description)
    VALUES ('茶文化深度体验月', NOW(), NOW() + INTERVAL '7 days', 'https://yauycf.top/root/images/event/tea_culture.png', TRUE, '为期一个月的茶文化主题活动，每周不同主题：台湾茶周、日本茶道周、英式下午茶周、创意调茶周。每日举办茶艺教学、品茶会、茶叶知识讲座。')
    RETURNING id INTO v_event_id;
    INSERT INTO "event_storearea" (event_id, storearea_id)
        SELECT v_event_id, s.id
        FROM "storearea" s
        JOIN "storearea_map" sm ON sm.storearea_id = s.id
        WHERE sm.map_id = v_map_id_floor1
            AND s.store_name IN ('F1-Store 018 TWININGS 皇家茶廊', 'F1-Store 008 鼎泰丰 小笼包专卖', 'F1-Store 015 Whole Foods Market 全食超市');
    INSERT INTO "event_eventarea" (event_id, eventarea_id)
        SELECT v_event_id, e.id
        FROM "eventarea" e
        JOIN "eventarea_map" em ON em.eventarea_id = e.id
        WHERE em.map_id = v_map_id_floor1
            AND e.description = '美食摊位区，设有20个标准摊位、公共用餐区。(Generated, Floor 1)';

    INSERT INTO "event" (event_name, start_date, end_date, image_url, is_active, description)
    VALUES ('圣诞魔法市集', NOW(), NOW() + INTERVAL '7 days', 'https://yauycf.top/root/images/event/christmas_market.png', TRUE, '全商场圣诞主题装饰，设置圣诞市集、圣诞老人屋、雪景拍照区、旋转木马。每日定时降雪秀、圣诞颂歌表演、圣诞礼物制作工作坊。')
    RETURNING id INTO v_event_id;
    INSERT INTO "event_storearea" (event_id, storearea_id)
        SELECT v_event_id, s.id
        FROM "storearea" s
        JOIN "storearea_map" sm ON sm.storearea_id = s.id
        WHERE sm.map_id = v_map_id_floor1
            AND s.store_name IN ('F1-Store 018 TWININGS 皇家茶廊', 'F1-Store 010 Cartier 卡地亚精品店', 'F1-Store 015 Whole Foods Market 全食超市');
    INSERT INTO "event_eventarea" (event_id, eventarea_id)
        SELECT v_event_id, e.id
        FROM "eventarea" e
        JOIN "eventarea_map" em ON em.eventarea_id = e.id
        WHERE em.map_id = v_map_id_floor1
            AND e.description = '长形走廊展示区，配备交互式触摸屏、VR体验站、智能家居模拟间及新品发布舞台。两侧设有品牌展示柜。(Generated, Floor 1)';

    INSERT INTO "event" (event_name, start_date, end_date, image_url, is_active, description)
    VALUES ('跨年倒数派对', NOW(), NOW() + INTERVAL '7 days', 'https://yauycf.top/root/images/event/newyear_party.png', TRUE, '跨年倒数狂欢派对，设有主舞台DJ表演、荧光舞池、新年许愿墙、跨年烟火秀。现场提供免费小食饮料，倒数时刻全场气球降落。')
    RETURNING id INTO v_event_id;
    INSERT INTO "event_storearea" (event_id, storearea_id)
        SELECT v_event_id, s.id
        FROM "storearea" s
        JOIN "storearea_map" sm ON sm.storearea_id = s.id
        WHERE sm.map_id = v_map_id_floor1
            AND s.store_name IN ('F1-Store 008 鼎泰丰 小笼包专卖', 'F1-Store 019 VR ZONE 虚拟实境乐园', 'F1-Store 003 星巴克 Reserve Bar');
    INSERT INTO "event_eventarea" (event_id, eventarea_id)
        SELECT v_event_id, e.id
        FROM "eventarea" e
        JOIN "eventarea_map" em ON em.eventarea_id = e.id
        WHERE em.map_id = v_map_id_floor1
            AND e.description = '长形走廊展示区，配备交互式触摸屏、VR体验站、智能家居模拟间及新品发布舞台。两侧设有品牌展示柜。(Generated, Floor 1)';

    INSERT INTO "event" (event_name, start_date, end_date, image_url, is_active, description)
    VALUES ('亲子运动会', NOW(), NOW() + INTERVAL '7 days', 'https://yauycf.top/root/images/event/family_sports.png', TRUE, '适合全家参与的趣味运动竞赛，包含亲子三腿赛跑、爸爸背小孩障碍赛、妈妈推婴儿车竞速。现场设有儿童游乐区、亲子按摩站。')
    RETURNING id INTO v_event_id;
    INSERT INTO "event_storearea" (event_id, storearea_id)
        SELECT v_event_id, s.id
        FROM "storearea" s
        JOIN "storearea_map" sm ON sm.storearea_id = s.id
        WHERE sm.map_id = v_map_id_floor1
            AND s.store_name IN ('F1-Store 005 Kidzania 儿童职业体验城', 'F1-Store 011 NIKE Rise 概念店', 'F1-Store 014 PETsMART 宠物百货');
    INSERT INTO "event_eventarea" (event_id, eventarea_id)
        SELECT v_event_id, e.id
        FROM "eventarea" e
        JOIN "eventarea_map" em ON em.eventarea_id = e.id
        WHERE em.map_id = v_map_id_floor1
            AND e.description = '可容纳200人的剧场，配备专业舞台灯光、音响系统、遮阳棚及阶梯式观众席。适合举办音乐会、话剧、舞蹈表演。(Generated, Floor 1)';

    INSERT INTO "event" (event_name, start_date, end_date, image_url, is_active, description)
    VALUES ('年货大街', NOW(), NOW() + INTERVAL '7 days', 'https://yauycf.top/root/images/event/newyear_market.png', TRUE, '年货采购市集，包含年节食品、春联红包、新年装饰、伴手礼盒。设有年菜试吃区、写春联服务、舞龙舞狮表演、财神爷发红包。')
    RETURNING id INTO v_event_id;
    INSERT INTO "event_storearea" (event_id, storearea_id)
        SELECT v_event_id, s.id
        FROM "storearea" s
        JOIN "storearea_map" sm ON sm.storearea_id = s.id
        WHERE sm.map_id = v_map_id_floor1
            AND s.store_name IN ('F1-Store 010 Cartier 卡地亚精品店', 'F1-Store 008 鼎泰丰 小笼包专卖', 'F1-Store 012 MUJI 家居生活馆');
    INSERT INTO "event_eventarea" (event_id, eventarea_id)
        SELECT v_event_id, e.id
        FROM "eventarea" e
        JOIN "eventarea_map" em ON em.eventarea_id = e.id
        WHERE em.map_id = v_map_id_floor1
            AND e.description = '通用活动区域。(Generated, Floor 1)';

END $$;

COMMIT;
