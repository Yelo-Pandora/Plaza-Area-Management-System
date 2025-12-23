/*
 * Benchmarking Data Generator for Indoor Map Project
 * Target: PostgreSQL / PostGIS
 * SRID: 2385
 */

BEGIN;

-- 1. 清理现有数据 (级联删除，小心使用)
TRUNCATE TABLE 
    "admin", 
    "event_storearea", "event_eventarea", "eventarea_map", "storearea_map", "facility_map", "otherarea_map",
    "event", "storearea", "eventarea", "facility", "otherarea", "map", "building" 
RESTART IDENTITY CASCADE;

-- 2. 插入管理员 (Admin)
-- 密码均为: password123
-- 注意：这里使用的是 Django默认的 PBKDF2_SHA256 哈希示例，实际使用时建议通过 Django shell 生成一个确切的
INSERT INTO "admin" (account, password, name) VALUES 
('admin', 'pbkdf2_sha256$260000$12345salt$jKqW1/8dK+XX+XX+XX+XX+XX+XX+XX+XX+XX+XX=', 'Super Admin'),
('manager', 'pbkdf2_sha256$260000$12345salt$jKqW1/8dK+XX+XX+XX+XX+XX+XX+XX+XX+XX+XX=', 'Store Manager');


-- 3. 使用 PL/pgSQL 动态生成海量数据
DO $$
DECLARE
    -- 变量定义
    v_building_id BIGINT;
    v_map_id BIGINT;
    v_store_id BIGINT;
    v_facility_id BIGINT;
    v_other_id BIGINT;
    v_eventarea_id BIGINT;
    v_event_id BIGINT;
    
    -- 循环变量
    f INT; -- Floor
    r INT; -- Row
    c INT; -- Column
    i INT;
    
    -- 几何计算变量
    x_base FLOAT;
    y_base FLOAT;
    geom_poly TEXT;
    geom_point TEXT;
    
BEGIN
    -- =========================================================
    -- A. 创建 1 个大型建筑 (Building)
    -- =========================================================
    INSERT INTO "building" (name, address, description) 
    VALUES ('Benchmark Mega Mall', '101 Tech Road, Taipei', 'A large shopping center for performance testing.')
    RETURNING id INTO v_building_id;

    RAISE NOTICE 'Building created with ID: %', v_building_id;

    -- =========================================================
    -- B. 创建 5 个楼层 (Map)
    -- 地图大小：200米 x 100米
    -- =========================================================
    FOR f IN 1..5 LOOP
        -- 创建 Map (detail 是 GeometryCollection，包含一个外框 Polyon)
        -- 外框: (0 0) -> (200 0) -> (200 100) -> (0 100) -> (0 0)
        INSERT INTO "map" (building_id, floor_number, detail)
        VALUES (
            v_building_id, 
            f, 
            ST_GeomFromText('GEOMETRYCOLLECTION(POLYGON((0 0, 200 0, 200 100, 0 100, 0 0)))', 2385)
        ) RETURNING id INTO v_map_id;

        -- =========================================================
        -- C. 在每个楼层生成网格状的 店铺 (Storearea)
        -- 网格：10行 x 4列，每个店铺 15x15米，间隔 5米
        -- =========================================================
        FOR r IN 0..3 LOOP -- 4行
            FOR c IN 0..9 LOOP -- 10列
                x_base := c * 20 + 2.5; -- x 起点
                y_base := r * 20 + 2.5; -- y 起点
                
                -- 构建 15x15 的正方形 WKT
                geom_poly := format('POLYGON((%s %s, %s %s, %s %s, %s %s, %s %s))', 
                    x_base, y_base, 
                    x_base + 15, y_base, 
                    x_base + 15, y_base + 15, 
                    x_base, y_base + 15, 
                    x_base, y_base
                );

                -- 插入 Storearea
                INSERT INTO "storearea" (
                    store_name, owner_name, owner_phone, logo_url, 
                    open_time, close_time, type, api_url, is_active, description, shape
                ) VALUES (
                    'Store F' || f || '-' || r || c, 
                    'Owner ' || c, 
                    '0912345678', 
                    'http://example.com/logo.png',
                    '09:00:00', '22:00:00', 
                    (c % 5) + 1, -- 类型 1-5 循环
                    NULL, 
                    TRUE, 
                    'Benchmark store description',
                    ST_GeomFromText(geom_poly, 2385)
                ) RETURNING id INTO v_store_id;

                -- 关联 StoreareaMap
                INSERT INTO "storearea_map" (storearea_id, map_id) VALUES (v_store_id, v_map_id);

            END LOOP;
        END LOOP;

        -- =========================================================
        -- D. 生成 设施 (Facility) (散落在走廊)
        -- =========================================================
        FOR i IN 1..10 LOOP
            x_base := (i * 18) + 5;
            y_base := 85; -- 放在上方走廊区域
            
            geom_point := format('POINT(%s %s)', x_base, y_base);
            
            INSERT INTO "facility" (type, is_active, description, location)
            VALUES (
                (i % 3) + 1, -- 类型 1:Restroom, 2:Elevator, 3:Exit
                TRUE,
                'Public Facility ' || i,
                ST_GeomFromText(geom_point, 2385)
            ) RETURNING id INTO v_facility_id;
            
            INSERT INTO "facility_map" (facility_id, map_id) VALUES (v_facility_id, v_map_id);
        END LOOP;

        -- =========================================================
        -- E. 生成 其他区域 (Otherarea) (例如楼梯、中庭)
        -- =========================================================
        INSERT INTO "otherarea" (type, is_public, is_active, description, shape)
        VALUES (
            1, TRUE, TRUE, 'Central Atrium Floor ' || f,
            ST_GeomFromText('POLYGON((80 40, 120 40, 120 60, 80 60, 80 40))', 2385)
        ) RETURNING id INTO v_other_id;
        
        INSERT INTO "otherarea_map" (otherarea_id, map_id) VALUES (v_other_id, v_map_id);

        -- =========================================================
        -- F. 生成 活动区域 (Eventarea) (临时展位)
        -- =========================================================
        INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape)
        VALUES (
            'Expo Org', '0988888888', 1, TRUE, 'Temp Booth Floor ' || f,
            ST_GeomFromText('POLYGON((180 80, 190 80, 190 90, 180 90, 180 80))', 2385)
        ) RETURNING id INTO v_eventarea_id;
        
        INSERT INTO "eventarea_map" (eventarea_id, map_id) VALUES (v_eventarea_id, v_map_id);

    END LOOP; -- 结束楼层循环

    -- =========================================================
    -- G. 生成 活动 (Event) 及其关联
    -- 跨越不同店铺的促销活动
    -- =========================================================
    FOR i IN 1..50 LOOP
        INSERT INTO "event" (event_name, start_date, end_date, image_url, is_active, description)
        VALUES (
            'Benchmark Event ' || i,
            NOW(), 
            NOW() + INTERVAL '7 days',
            'http://example.com/event.jpg',
            TRUE,
            'Huge sale event number ' || i
        ) RETURNING id INTO v_event_id;

        -- 随机关联 3 个店铺到这个活动
        INSERT INTO "event_storearea" (event_id, storearea_id)
        SELECT v_event_id, id FROM "storearea" 
        ORDER BY RANDOM() LIMIT 3;
        
        -- 随机关联 1 个活动区域
        INSERT INTO "event_eventarea" (event_id, eventarea_id)
        SELECT v_event_id, id FROM "eventarea"
        ORDER BY RANDOM() LIMIT 1;
    END LOOP;

END $$;

COMMIT;