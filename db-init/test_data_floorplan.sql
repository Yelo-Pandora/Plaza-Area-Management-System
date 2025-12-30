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
('admin', 'pbkdf2_sha256$1000000$980cOulSX3vlCCloSs2ove$66ySapvBsD5+8e54mupZt9S0nt9Eol7f7F/2jDUDQKQ=', 'Super Admin'),
('manager', 'pbkdf2_sha256$1000000$980cOulSX3vlCCloSs2ove$66ySapvBsD5+8e54mupZt9S0nt9Eol7f7F/2jDUDQKQ=', 'Store Manager');

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
        '/images/store/UR.png',
        '10:00:00', '22:00:00',
        2,
        NULL,
        TRUE,
        '国际设计师品牌集合店，主打简约时尚与街头文化融合。每月第一周举行设计师见面会。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((145.455 19.414, 144.838 13.559, 144.222 13.251, 144.222 10.478, 144.838 9.861, 157.473 8.629, 158.089 13.251, 158.706 13.559, 158.706 16.949, 158.089 17.565, 145.455 19.414))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 002 Apple Store Taipei 101',
        'F' || v_floor || '-Owner 002 张致远',
        '0918-888-999',
        '/images/store/apple.png',
        '10:00:00', '22:00:00',
        3,
        NULL,
        TRUE,
        '苹果直营店，提供最新产品体验、Today at Apple工作坊、Genius Bar技术支持服务。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((95.532 26.81, 96.148 22.804, 100.462 16.641, 124.807 14.176, 125.424 22.496, 95.532 26.81))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 003 星巴克 Reserve Bar',
        'F' || v_floor || '-Owner 003 林雅婷',
        '0920-555-666',
        '/images/store/星巴克.png',
        '07:00:00', '23:00:00',
        1,
        NULL,
        TRUE,
        '星巴克臻选店，提供稀有咖啡豆手冲服务，每月举办咖啡品鉴会，设有露天座位区。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((77.042 27.427, 75.809 12.943, 78.582 12.943, 81.356 14.792, 90.293 16.641, 90.909 19.414, 89.676 20.955, 89.676 22.496, 88.444 22.804, 88.444 25.578, 77.042 27.427))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 004 Sephora 亚洲旗舰店',
        'F' || v_floor || '-Owner 004 王诗涵',
        '0933-777-888',
        '/images/store/sephora.png',
        '11:00:00', '22:00:00',
        4,
        NULL,
        TRUE,
        '美妆概念店，提供AR试妆、专业彩妆咨询、个性化护肤方案，设有美妆教学区。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((56.703 22.496, 56.703 20.955, 57.319 20.339, 68.721 19.723, 69.337 27.427, 68.721 28.043, 65.331 28.043, 65.023 28.659, 60.401 28.659, 60.401 27.735, 59.168 27.427, 59.168 26.502, 56.703 22.496))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 005 Kidzania 儿童职业体验城',
        'F' || v_floor || '-Owner 005 黄志明',
        '0910-123-456',
        '/images/store/KidZania.png',
        '09:30:00', '20:30:00',
        3,
        NULL,
        TRUE,
        '专为3-14岁儿童设计的职业体验乐园，设有消防局、电视台、银行等20+职业模拟场景。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((114.33 40.37, 107.242 40.986, 107.242 38.213, 105.701 37.288, 102.928 37.288, 102.619 39.137, 90.601 39.753, 90.601 35.747, 92.45 32.049, 99.846 30.817, 105.085 32.049, 105.393 30.2, 114.33 29.584, 114.33 40.37))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 006 诚品生活 Eslite Spectrum',
        'F' || v_floor || '-Owner 006 吴嘉豪',
        '0922-333-444',
        '/images/store/诚品生活.png',
        '10:00:00', '24:00:00',
        0,
        NULL,
        TRUE,
        '24小时营业的文化复合空间，包含书店、文创商品、咖啡厅、展览空间和讲座区。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((131.279 42.219, 131.279 35.131, 133.128 34.515, 154.391 35.131, 153.159 42.219, 131.279 42.219))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 007 World Gym 科技旗舰店',
        'F' || v_floor || '-Owner 007 刘建华',
        '0935-678-901',
        '/images/store/world gym.png',
        '06:00:00', '24:00:00',
        4,
        NULL,
        TRUE,
        '配备智能健身设备、VR动感单车、专业拳击台、空中瑜伽教室及营养咨询中心。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((84.129 61.941, 81.972 61.941, 81.972 59.784, 80.123 58.86, 80.123 33.282, 83.513 33.282, 84.129 37.596, 84.129 61.941))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 008 鼎泰丰 小笼包专卖',
        'F' || v_floor || '-Owner 008 李正元',
        '0916-789-012',
        '/images/store/鼎泰丰.png',
        '11:00:00', '21:00:00',
        1,
        NULL,
        TRUE,
        '米其林一星餐厅美食广场分店，提供招牌小笼包、红油抄手、排骨炒饭等经典餐点。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((67.488 75.501, 61.633 75.501, 61.017 70.878, 57.319 70.57, 57.011 65.639, 50.539 65.639, 50.539 60.401, 47.458 59.476, 47.458 45.609, 44.376 45.3, 44.992 34.515, 50.847 32.666, 61.325 55.47, 67.488 75.501))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 009 Studio A 苹果授权经销商',
        'F' || v_floor || '-Owner 009 蔡文杰',
        '0925-456-789',
        '/images/store/Studio A苹果授权经销商.png',
        '11:00:00', '21:30:00',
        0,
        NULL,
        TRUE,
        '苹果授权维修中心，提供原厂配件、专业维修服务、企业采购咨询及教育优惠办理。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((149.769 76.117, 150.385 69.646, 157.781 58.86, 157.781 42.527, 167.951 42.527, 167.951 44.684, 170.416 46.225, 168.567 52.08, 172.265 53.621, 172.265 75.501, 149.769 76.117))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 010 Cartier 卡地亚精品店',
        'F' || v_floor || '-Owner 010 法国总部直营',
        '+33158181800',
        '/images/store/卡地亚.png',
        '11:00:00', '20:00:00',
        0,
        NULL,
        TRUE,
        '法国奢侈品牌卡地亚专门店，提供高级珠宝、腕表、皮具及婚礼系列，设有VIP贵宾室。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((142.373 92.142, 146.687 80.123, 166.102 80.123, 165.485 92.758, 157.781 92.142, 157.473 94.607, 155.932 94.607, 155.008 92.142, 142.373 92.142))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 011 NIKE Rise 概念店',
        'F' || v_floor || '-Owner 011 王健雄',
        '0930-111-222',
        '/images/store/NIKE rise.png',
        '09:00:00', '22:00:00',
        2,
        NULL,
        TRUE,
        '亚洲首家Nike Rise概念店，提供3D足部扫描定制鞋垫、AR虚拟试衣间、运动数据分析服务。设有篮球测试区与跑步机体验区。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((200.0 96.456, 193.529 97.072, 193.529 88.136, 185.516 86.595, 185.516 81.972, 187.365 80.431, 187.365 73.344, 200.0 73.344, 200.0 96.456))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 012 MUJI 家居生活馆',
        'F' || v_floor || '-Owner 012 李佳蓉',
        '0915-333-444',
        '/images/store/MUJI无印良品.png',
        '10:30:00', '22:00:00',
        3,
        NULL,
        TRUE,
        '包含家具展示间、食品贩卖区、服装定制服务、书籍区及Café&Meal MUJI餐厅。提供家具配置咨询服务。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((132.82 98.305, 115.871 100.154, 89.368 90.909, 88.752 49.307, 100.154 50.539, 100.154 57.011, 91.525 57.935, 91.525 68.721, 99.538 89.676, 134.669 89.985, 134.977 82.589, 127.581 78.582, 129.43 51.772, 145.763 52.388, 145.146 69.954, 132.82 98.305))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 013 松本清 Matsumoto Kiyoshi',
        'F' || v_floor || '-Owner 013 田中一郎',
        '0919-555-666',
        '/images/store/松本清.png',
        '09:00:00', '22:00:00',
        4,
        NULL,
        TRUE,
        '日本知名药妆连锁店台湾首店，提供3000多种日本直送药品、化妆品、健康食品。设有免税柜台及日语咨询服务。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((34.515 114.33, 41.294 108.166, 41.294 97.997, 58.86 99.23, 59.784 89.985, 64.715 89.06, 64.715 81.972, 70.57 81.972, 72.419 97.689, 69.337 97.997, 66.872 106.317, 63.79 108.166, 46.225 108.783, 38.213 112.481, 37.288 114.946, 34.515 114.33))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 014 PETsMART 宠物百货',
        'F' || v_floor || '-Owner 014 陈爱宠',
        '0928-777-888',
        '/images/store/petsMART.png',
        '10:00:00', '21:30:00',
        5,
        NULL,
        TRUE,
        '宠物百货，提供宠物食品、玩具、服饰、美容服务、医疗咨询、宠物旅馆。设有宠物游泳池及训练场。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((74.884 127.273, 72.727 127.889, 72.419 126.04, 65.331 126.04, 63.79 124.807, 57.935 124.807, 57.319 124.191, 57.319 120.801, 73.652 118.952, 74.884 119.569, 74.884 127.273))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 015 Whole Foods Market 全食超市',
        'F' || v_floor || '-Owner 015 张健康',
        '0932-999-000',
        '/images/store/wholeFoodsMarket-logo.png',
        '08:00:00', '22:00:00',
        1,
        NULL,
        TRUE,
        '美国有机超市品牌亚洲首店，提供有机蔬果、无添加食品、公平贸易咖啡、现做沙拉吧、果汁吧及有机熟食。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((11.094 127.889, 7.396 116.179, 6.78 110.94, 13.251 109.707, 22.188 114.022, 24.345 114.022, 24.961 119.26, 23.421 119.26, 21.88 122.342, 16.025 123.575, 15.1 127.273, 11.094 127.889))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 016 B&O Play 听觉实验室',
        'F' || v_floor || '-Owner 016 林音悦',
        '0911-222-333',
        '/images/store/B&O Play.png',
        '11:00:00', '22:00:00',
        2,
        NULL,
        TRUE,
        '丹麦奢华音响品牌体验店，设有7间不同声学设计的试听室、私人影院体验区、音响定制咨询服务。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((197.535 142.065, 189.831 145.763, 163.328 130.971, 151.618 121.726, 140.524 101.695, 157.473 104.16, 157.781 107.242, 161.171 107.242, 161.479 117.72, 180.894 120.185, 182.435 128.197, 189.522 125.732, 189.522 134.669, 197.535 134.977, 197.535 142.065))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 017 Hands Craft Studio 手作实验室',
        'F' || v_floor || '-Owner 017 王艺师',
        '0920-444-555',
        '/images/store/Hands Craft.png',
        '11:00:00', '21:00:00',
        3,
        NULL,
        TRUE,
        '提供皮革制作、金工体验、陶艺创作、木工DIY等手作课程。材料齐全，专业导师指导，可制作个人专属作品。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((119.569 115.871, 134.052 117.72, 129.738 119.569, 131.895 125.116, 134.977 124.807, 136.518 119.569, 144.53 126.348, 144.53 130.354, 139.599 133.128, 139.908 139.291, 149.461 139.291, 151.31 131.895, 157.165 139.291, 172.265 144.838, 169.183 150.693, 120.801 150.693, 119.569 115.871))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 018 TWININGS 皇家茶廊',
        'F' || v_floor || '-Owner 018 英国总部直营',
        '+442073520000',
        '/images/store/TWININGS.png',
        '09:00:00', '22:00:00',
        4,
        NULL,
        TRUE,
        '英国300年历史茶品牌，提供超过100种茶叶选择、茶具贩卖、茶艺教学、英式下午茶体验服务。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((81.356 150.693, 80.74 118.336, 114.946 115.871, 115.562 124.191, 100.154 124.499, 100.154 133.436, 103.852 133.744, 104.468 140.216, 107.242 142.373, 114.33 142.989, 114.33 150.693, 81.356 150.693))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 019 VR ZONE 虚拟实境乐园',
        'F' || v_floor || '-Owner 019 陈科技',
        '0917-666-777',
        '/images/store/VR ZONE.png',
        '09:00:00', '22:00:00',
        5,
        NULL,
        TRUE,
        '亚洲最大VR体验中心，提供20+种VR游戏、恐怖体验、飞行模拟、赛车竞技。适合个人、情侣、团体体验。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((55.47 150.077, 55.47 139.291, 73.652 139.291, 71.803 150.693, 56.086 150.693, 55.47 150.077))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "storearea" (
        store_name, owner_name, owner_phone, logo_url,
        open_time, close_time, type, api_url, is_active, description, shape
    ) VALUES (
        'F' || v_floor || '-Store 020 海马体 HIMO 证件照专门店',
        'F' || v_floor || '-Owner 020 林摄影',
        '0925-888-999',
        '/images/store/海马体.png',
        '09:40:00', '22:40:00',
        1,
        NULL,
        TRUE,
        '专业证件照、形象照拍摄，提供化妆、造型、修图一站式服务。设有8种主题摄影棚，最快2小时取件。(Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((23.421 144.53, 20.955 133.744, 31.741 130.663, 41.911 124.499, 53.929 122.034, 54.545 134.669, 50.231 132.82, 39.137 133.744, 39.445 139.291, 50.847 139.908, 50.847 150.693, 31.433 150.693, 23.421 144.53))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_id, v_map_id);

    -- Otherareas extracted from image
    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        1, TRUE, TRUE,
        'Other Area 01 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((55.47 11.094, 60.092 11.094, 60.401 10.478, 61.941 10.478, 61.941 13.251, 62.866 14.176, 70.57 14.176, 70.57 18.798, 63.482 18.798, 63.174 19.414, 59.784 19.414, 59.784 13.559, 55.47 13.251, 55.47 11.094))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        1, TRUE, TRUE,
        'Other Area 02 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((97.997 30.508, 97.997 27.119, 106.934 26.502, 107.242 25.886, 115.562 25.27, 119.569 24.037, 124.191 24.037, 124.191 27.427, 115.871 27.427, 115.562 28.659, 109.707 28.659, 109.399 29.276, 105.393 29.276, 103.236 30.508, 97.997 30.508))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        3, TRUE, TRUE,
        'Other Area 03 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((43.451 46.533, 41.294 46.533, 41.294 41.911, 40.062 39.753, 40.678 37.288, 40.062 17.874, 42.219 17.874, 45.917 20.955, 50.231 30.2, 50.231 32.357, 48.074 32.357, 43.451 34.515, 43.451 46.533))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        0, TRUE, TRUE,
        'Other Area 04 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((146.687 62.558, 146.687 60.401, 148.536 60.092, 148.536 54.854, 146.071 54.545, 146.071 51.156, 147.92 50.847, 148.536 48.074, 151.926 47.458, 151.926 49.615, 154.391 49.923, 154.391 58.243, 155.624 58.552, 155.624 62.558, 146.687 62.558))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        0, TRUE, TRUE,
        'Other Area 05 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((179.969 66.872, 179.353 58.552, 172.573 56.394, 170.108 38.829, 177.504 31.741, 177.504 27.735, 168.259 26.194, 167.643 22.804, 164.561 21.88, 166.41 12.943, 163.945 6.78, 195.686 0.616, 200.0 1.849, 200.0 52.08, 195.994 52.08, 192.604 56.703, 192.604 66.872, 179.969 66.872))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        0, TRUE, TRUE,
        'Other Area 06 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((69.029 75.501, 56.703 41.911, 66.256 38.213, 66.564 35.747, 79.199 33.282, 79.199 59.476, 84.746 59.784, 84.746 63.174, 82.897 63.482, 82.897 75.501, 69.029 75.501))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        0, TRUE, TRUE,
        'Other Area 07 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((100.462 89.06, 99.846 79.507, 94.299 79.199, 92.45 57.935, 101.079 57.627, 100.462 47.458, 104.777 46.533, 104.777 41.911, 122.958 41.294, 125.732 29.584, 130.971 29.584, 126.656 76.117, 129.738 76.425, 130.046 83.205, 134.052 83.205, 134.052 89.06, 117.72 89.06, 117.411 90.909, 100.462 89.06))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        0, TRUE, TRUE,
        'Other Area 08 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((0.0 101.387, 0.0 81.356, 55.778 81.356, 56.086 71.495, 60.092 71.495, 60.092 79.199, 63.79 79.507, 63.79 88.444, 55.778 91.834, 55.778 98.921, 40.678 97.072, 40.37 108.166, 34.823 113.097, 32.049 113.097, 31.741 98.305, 27.427 98.613, 27.427 110.015, 25.27 110.015, 24.961 105.085, 0.0 101.387))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        0, TRUE, TRUE,
        'Other Area 09 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((190.139 124.807, 182.435 127.273, 182.126 119.26, 161.479 116.795, 161.479 106.626, 157.473 102.619, 142.989 102.619, 140.524 105.085, 140.524 100.462, 157.781 100.154, 157.473 95.223, 143.606 95.223, 143.606 92.45, 166.718 93.066, 167.026 80.74, 172.881 80.74, 173.19 76.425, 176.579 76.425, 177.504 81.972, 184.592 81.972, 184.9 88.136, 192.604 88.136, 192.604 97.072, 185.208 97.381, 185.208 114.946, 190.139 115.254, 190.139 124.807))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        2, TRUE, TRUE,
        'Other Area 10 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((140.524 138.367, 140.524 133.128, 143.297 133.128, 143.606 131.895, 144.53 131.895, 145.455 130.971, 145.455 129.43, 149.461 129.43, 149.461 132.203, 148.844 132.512, 148.844 138.367, 140.524 138.367))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        1, TRUE, TRUE,
        'Other Area 11 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((40.062 138.367, 40.062 133.744, 50.231 133.744, 50.539 135.593, 55.47 135.285, 54.854 120.801, 57.011 120.801, 57.319 125.732, 71.803 126.965, 72.111 128.814, 74.884 128.814, 74.268 138.367, 40.062 138.367))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
    VALUES (
        2, TRUE, TRUE,
        'Other Area 12 (Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((107.242 142.065, 107.242 139.908, 104.777 139.599, 104.777 133.128, 101.079 132.82, 101.079 125.116, 115.562 125.116, 115.562 139.599, 114.946 139.908, 114.946 142.065, 107.242 142.065))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_id, v_map_id);

    -- Eventareas extracted from image
    INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape)
    VALUES (
        '文化局', '02-2345-6789', 3, TRUE,
        '可容纳200人的剧场，配备专业舞台灯光、音响系统、遮阳棚及阶梯式观众席。适合举办音乐会、话剧、舞蹈表演。(Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((102.928 38.521, 102.928 32.049, 102.311 31.741, 102.311 30.2, 105.085 30.2, 105.085 38.521, 102.928 38.521))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "eventarea_map" (eventarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape)
    VALUES (
        '科学教育馆', '02-1122-3344', 1, TRUE,
        '互动科学实验区，配备物理实验装置、化学实验台、天文望远镜及机器人编程工作站。(Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((88.752 68.721, 88.752 57.319, 92.142 57.319, 92.142 68.721, 88.752 68.721))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "eventarea_map" (eventarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape)
    VALUES (
        '购物中心', '02-1234-5678', 1, TRUE,
        '通用活动区域。(Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((126.965 79.199, 126.965 75.193, 132.203 75.193, 132.203 77.35, 130.663 77.35, 130.354 79.199, 126.965 79.199))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "eventarea_map" (eventarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape)
    VALUES (
        '购物中心', '02-1234-5678', 2, TRUE,
        '长形走廊展示区，配备交互式触摸屏、VR体验站、智能家居模拟间及新品发布舞台。两侧设有品牌展示柜。(Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((147.92 79.815, 147.92 75.193, 149.461 75.193, 149.769 76.425, 166.718 76.425, 166.718 79.815, 147.92 79.815))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "eventarea_map" (eventarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape)
    VALUES (
        '美食节筹委会', '0928-888-999', 1, TRUE,
        '美食摊位区，设有20个标准摊位、公共用餐区。(Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((32.666 113.713, 32.666 112.173, 39.137 112.173, 39.137 113.713, 37.288 115.562, 35.131 115.562, 32.666 113.713))', 2385)
    ) RETURNING id INTO v_id;
    INSERT INTO "eventarea_map" (eventarea_id, map_id) VALUES (v_id, v_map_id);

    INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape)
    VALUES (
        '创客协会', '02-3456-7890', 2, TRUE,
        '配备10个工作台，每台配备3D打印机、激光切割机、电子焊接设备，设有材料储存区及作品展示墙。(Generated, Floor ' || v_floor || ')',
        ST_GeomFromText('POLYGON((134.052 126.04, 132.512 126.04, 132.512 125.116, 131.895 124.807, 131.895 122.65, 129.43 121.726, 129.43 120.185, 130.046 119.877, 130.046 117.103, 133.436 117.103, 133.744 117.72, 134.669 117.72, 136.518 118.952, 136.518 120.493, 134.669 120.801, 134.669 125.424, 134.052 126.04))', 2385)
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
    VALUES ('万圣节惊奇派对', NOW(), NOW() + INTERVAL '7 days', '/images/event/万圣节派对.png', TRUE, '万圣节主题狂欢派对，包含鬼屋探险、变装比赛、南瓜雕刻工作坊、不给糖就捣蛋路线。现场提供免费化妆服务、恐怖主题美食摊位。')
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
    VALUES ('科技新品发布', NOW(), NOW() + INTERVAL '7 days', '/images/event/科技新品发布.png', TRUE, '深度融合“展示、销售、互动、体验”，打造沉浸式场景。')
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
    VALUES ('2024毛小孩时装周', NOW(), NOW() + INTERVAL '7 days', '/images/event/毛孩子时装周.png', TRUE, '宠物时装走秀比赛，设有创意造型组、亲子配对组、最佳才艺组。现场提供宠物美容服务、摄影棚、领养服务摊位。冠军可获得宠物百货购物金1万元。')
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
    VALUES ('有机生活节', NOW(), NOW() + INTERVAL '7 days', '/images/event/有机生活节.png', TRUE, '倡导环保永续生活方式，包含有机农产品展售、零废弃工作坊、环保手作体验、绿色饮食讲座。现场设有二手物交换站、环保杯租借服务。')
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
    VALUES ('电竞狂欢节', NOW(), NOW() + INTERVAL '7 days', '/images/event/电竞狂欢节.png', TRUE, '专业比赛舞台配备实时转播，现场提供电竞设备体验区、选手签名会。')
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
    VALUES ('冰品嘉年华', NOW(), NOW() + INTERVAL '7 days', '/images/event/冰雪嘉年华.png', TRUE, '汇聚20家特色冰品摊位，包含传统刨冰、创意冰淇淋、冻饮调酒。设有冰品造型比赛、大胃王挑战、DIY冰淇淋工作坊。')
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
    VALUES ('小小科学家夏令营', NOW(), NOW() + INTERVAL '7 days', '/images/event/小小科学家.png', TRUE, '科学主题夏令营，每日不同主题：化学实验日、机器人编程日、天文观测日、生态探索日、科学成果展。适合7-12岁儿童参加。')
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
    VALUES ('时尚艺术周', NOW(), NOW() + INTERVAL '7 days', '/images/event/时尚艺术周.png', TRUE, '结合时尚与艺术的跨界活动，包含新锐设计师时装秀、艺术装置展览、街头艺术创作、时尚摄影展。设有设计师对谈会及workshop。')
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
    VALUES ('茶文化深度体验月', NOW(), NOW() + INTERVAL '7 days', '/images/event/茶文化深度体验.png', TRUE, '为期一个月的茶文化主题活动，每周不同主题：台湾茶周、日本茶道周、英式下午茶周、创意调茶周。每日举办茶艺教学、品茶会、茶叶知识讲座。')
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
    VALUES ('圣诞魔法市集', NOW(), NOW() + INTERVAL '7 days', '/images/event/圣诞魔法市集.png', TRUE, '全商场圣诞主题装饰，设置圣诞市集、圣诞老人屋、雪景拍照区、旋转木马。每日定时降雪秀、圣诞颂歌表演、圣诞礼物制作工作坊。')
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
    VALUES ('跨年倒数派对', NOW(), NOW() + INTERVAL '7 days', '/images/event/跨年派对.png', TRUE, '跨年倒数狂欢派对，设有主舞台DJ表演、荧光舞池、新年许愿墙、跨年烟火秀。现场提供免费小食饮料，倒数时刻全场气球降落。')
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
    VALUES ('亲子运动会', NOW(), NOW() + INTERVAL '7 days', '/images/event/亲子运动会.png', TRUE, '适合全家参与的趣味运动竞赛，包含亲子三腿赛跑、爸爸背小孩障碍赛、妈妈推婴儿车竞速。现场设有儿童游乐区、亲子按摩站。')
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
    VALUES ('年货大街', NOW(), NOW() + INTERVAL '7 days', '/images/event/年货大街.png', TRUE, '年货采购市集，包含年节食品、春联红包、新年装饰、伴手礼盒。设有年菜试吃区、写春联服务、舞龙舞狮表演、财神爷发红包。')
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