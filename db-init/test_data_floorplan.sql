/*
 * Optimized Plaza Layout V2
 * Target: PostgreSQL / PostGIS (SRID: 2385)
 * 
 * Logic:
 * - Map Size: Approx 200 x 150
 * - Layout: 4 Quadrants separated by a central cross corridor (width 20).
 * - Preservation: Keeps all 20 Stores, 12 OtherAreas, 6 EventAreas, 18 Facilities.
 */

BEGIN;

-- 1. Clean up
TRUNCATE TABLE 
    "admin",
    "event_storearea", "event_eventarea", "eventarea_map", "storearea_map", "facility_map", "otherarea_map",
    "event", "storearea", "eventarea", "facility", "otherarea", "map", "building"
RESTART IDENTITY CASCADE;

-- 2. Admins
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
    v_corridor_geom TEXT;
BEGIN
    -- 3. Building
    INSERT INTO "building" (name, address, description)
    VALUES ('Benchmark Mega Mall', '101 Tech Road, Taipei', 'Optimized High-Traffic Plaza')
    RETURNING id INTO v_building_id;

    -- 4. Generate Floors
    FOR v_floor IN 1..4 LOOP
        
        -- Map: Keep the original complex contour
        INSERT INTO "map" (building_id, floor_number, detail)
        VALUES (
            v_building_id,
            v_floor,
            ST_GeomFromText('GEOMETRYCOLLECTION(POLYGON((21.572 143.914, 19.106 128.814, 9.861 127.889, 3.698 105.393, 0.0 105.085, 0.0 80.74, 56.086 80.431, 56.086 66.564, 49.923 66.256, 49.923 61.017, 46.841 60.709, 46.841 47.458, 40.678 46.533, 40.678 12.327, 61.941 10.478, 62.866 14.176, 78.582 12.327, 91.834 17.874, 130.354 13.559, 131.279 33.898, 158.089 34.515, 159.014 40.062, 169.8 40.062, 175.039 34.206, 175.039 27.735, 147.92 23.112, 147.612 20.647, 144.222 20.647, 143.606 9.861, 163.636 8.012, 165.794 4.931, 189.831 0.0, 200.0 0.616, 200.0 52.08, 196.61 52.08, 192.604 57.319, 192.604 71.803, 200.0 72.111, 200.0 97.689, 195.069 97.997, 195.069 114.946, 190.139 115.254, 190.755 133.436, 200.0 134.361, 200.0 143.914, 189.214 146.379, 183.359 142.681, 176.888 142.681, 169.183 151.926, 31.433 151.926, 21.572 143.914)))', 2385)
        ) RETURNING id INTO v_map_id;

        IF v_floor = 1 THEN
            v_map_id_floor1 := v_map_id;
        END IF;

        -- ======================================================
        -- LAYOUT STRATEGY (Grid System)
        -- Quadrant 1 (Top-Left): X[20-80], Y[20-60]
        -- Quadrant 2 (Top-Right): X[120-180], Y[20-60]
        -- Quadrant 3 (Bottom-Left): X[20-80], Y[90-130]
        -- Quadrant 4 (Bottom-Right): X[120-180], Y[90-130]
        -- Center: X[80-120], Y[60-90] -> Event Atrium
        -- Corridors: Between quadrants
        -- ======================================================

        -- --- STORES (20 Count) ---
        
        -- Q1: Top-Left (5 Stores)
        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-001 URBAN STYLE', 'Owner 1', 2, TRUE, 'Q1 Main',
         ST_GeomFromText('POLYGON((20 20, 50 20, 50 40, 20 40, 20 20))', 2385), 'https://yauycf.top/root/images/store/UR.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-002 Apple Store', 'Owner 2', 3, TRUE, 'Q1 Anchor',
         ST_GeomFromText('POLYGON((55 20, 80 20, 80 40, 55 40, 55 20))', 2385), 'https://yauycf.top/root/images/store/apple.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-003 Starbucks', 'Owner 3', 1, TRUE, 'Q1 Corner',
         ST_GeomFromText('POLYGON((20 45, 40 45, 40 60, 20 60, 20 45))', 2385), 'https://yauycf.top/root/images/store/starbucks.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-004 Sephora', 'Owner 4', 4, TRUE, 'Q1 Inner',
         ST_GeomFromText('POLYGON((45 45, 60 45, 60 60, 45 60, 45 45))', 2385), 'https://yauycf.top/root/images/store/sephora.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-005 Kidzania', 'Owner 5', 3, TRUE, 'Q1 Inner',
         ST_GeomFromText('POLYGON((65 45, 80 45, 80 60, 65 60, 65 45))', 2385), 'https://yauycf.top/root/images/store/KidZania.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        -- Q2: Top-Right (5 Stores)
        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-006 Eslite', 'Owner 6', 0, TRUE, 'Q2 Main',
         ST_GeomFromText('POLYGON((120 20, 150 20, 150 40, 120 40, 120 20))', 2385), 'https://yauycf.top/root/images/store/eslite.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-007 World Gym', 'Owner 7', 4, TRUE, 'Q2 Anchor',
         ST_GeomFromText('POLYGON((155 20, 185 20, 185 45, 155 45, 155 20))', 2385), 'https://yauycf.top/root/images/store/world gym.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-008 Din Tai Fung', 'Owner 8', 1, TRUE, 'Q2 Side',
         ST_GeomFromText('POLYGON((120 45, 140 45, 140 60, 120 60, 120 45))', 2385), 'https://yauycf.top/root/images/store/dingtaifeng.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-009 Studio A', 'Owner 9', 0, TRUE, 'Q2 Side',
         ST_GeomFromText('POLYGON((145 45, 160 45, 160 60, 145 60, 145 45))', 2385), 'https://yauycf.top/root/images/store/studio_a.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-010 Cartier', 'Owner 10', 0, TRUE, 'Q2 Side',
         ST_GeomFromText('POLYGON((165 50, 185 50, 185 65, 165 65, 165 50))', 2385), 'https://yauycf.top/root/images/store/cartier.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        -- Q3: Bottom-Left (5 Stores)
        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-011 NIKE Rise', 'Owner 11', 2, TRUE, 'Q3 Main',
         ST_GeomFromText('POLYGON((20 90, 50 90, 50 115, 20 115, 20 90))', 2385), 'https://yauycf.top/root/images/store/NIKE rise.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-012 MUJI', 'Owner 12', 3, TRUE, 'Q3 Side',
         ST_GeomFromText('POLYGON((55 90, 80 90, 80 110, 55 110, 55 90))', 2385), 'https://yauycf.top/root/images/store/muji.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-013 Matsumoto', 'Owner 13', 4, TRUE, 'Q3 Corner',
         ST_GeomFromText('POLYGON((20 120, 45 120, 45 140, 20 140, 20 120))', 2385), 'https://yauycf.top/root/images/store/matsumoto_kiyoshi.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-014 PETsMART', 'Owner 14', 5, TRUE, 'Q3 Side',
         ST_GeomFromText('POLYGON((50 115, 70 115, 70 140, 50 140, 50 115))', 2385), 'https://yauycf.top/root/images/store/petsMART.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-015 Whole Foods', 'Owner 15', 1, TRUE, 'Q3 Side',
         ST_GeomFromText('POLYGON((75 115, 95 115, 95 135, 75 135, 75 115))', 2385), 'https://yauycf.top/root/images/store/wholeFoodsMarket-logo.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        -- Q4: Bottom-Right (5 Stores)
        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-016 B&O Play', 'Owner 16', 2, TRUE, 'Q4 Anchor',
         ST_GeomFromText('POLYGON((120 90, 155 90, 155 115, 120 115, 120 90))', 2385), 'https://yauycf.top/root/images/store/B&O Play.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-017 Hands Craft', 'Owner 17', 3, TRUE, 'Q4 Side',
         ST_GeomFromText('POLYGON((160 90, 185 90, 185 110, 160 110, 160 90))', 2385), 'https://yauycf.top/root/images/store/Hands Craft.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-018 TWININGS', 'Owner 18', 4, TRUE, 'Q4 Side',
         ST_GeomFromText('POLYGON((120 120, 140 120, 140 140, 120 140, 120 120))', 2385), 'https://yauycf.top/root/images/store/TWININGS.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-019 VR ZONE', 'Owner 19', 5, TRUE, 'Q4 Side',
         ST_GeomFromText('POLYGON((145 120, 165 120, 165 140, 145 140, 145 120))', 2385), 'https://yauycf.top/root/images/store/VR ZONE.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);

        INSERT INTO "storearea" (store_name, owner_name, type, is_active, description, shape, logo_url) VALUES 
        ('F' || v_floor || '-020 HIMO', 'Owner 20', 1, TRUE, 'Q4 Corner',
         ST_GeomFromText('POLYGON((170 115, 190 115, 190 135, 170 135, 170 115))', 2385), 'https://yauycf.top/root/images/store/haimaiti.png') RETURNING id INTO v_id; 
         INSERT INTO "storearea_map" VALUES (v_id, v_map_id);


        -- --- OTHER AREAS (12 Count) ---
        -- Restrooms & Offices & Public Fillers
        
        -- 01. Restroom Top-Left Corner
        INSERT INTO "otherarea" (type, is_public, is_active, description, shape) VALUES (
            1, TRUE, TRUE, 'Restroom NW', ST_GeomFromText('POLYGON((5 15, 15 15, 15 30, 5 30, 5 15))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "otherarea_map" VALUES (v_id, v_map_id);

        -- 02. Restroom Bottom-Right Corner
        INSERT INTO "otherarea" (type, is_public, is_active, description, shape) VALUES (
            1, TRUE, TRUE, 'Restroom SE', ST_GeomFromText('POLYGON((185 130, 195 130, 195 145, 185 145, 185 130))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "otherarea_map" VALUES (v_id, v_map_id);

        -- 03. Office Top-Right
        INSERT INTO "otherarea" (type, is_public, is_active, description, shape) VALUES (
            1, FALSE, TRUE, 'Admin Office', ST_GeomFromText('POLYGON((180 5, 195 5, 195 15, 180 15, 180 5))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "otherarea_map" VALUES (v_id, v_map_id);

        -- 04. Storage Left-Mid
        INSERT INTO "otherarea" (type, is_public, is_active, description, shape) VALUES (
            2, FALSE, TRUE, 'Storage Room A', ST_GeomFromText('POLYGON((5 60, 15 60, 15 75, 5 75, 5 60))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "otherarea_map" VALUES (v_id, v_map_id);

        -- 05. Equipment Room Right-Mid
        INSERT INTO "otherarea" (type, is_public, is_active, description, shape) VALUES (
            2, FALSE, TRUE, 'Server Room', ST_GeomFromText('POLYGON((185 60, 195 60, 195 75, 185 75, 185 60))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "otherarea_map" VALUES (v_id, v_map_id);

        -- 06-11. Small Filler/Kiosks areas (Distributed)
        INSERT INTO "otherarea" (type, is_public, is_active, description, shape) VALUES (
            3, TRUE, TRUE, 'Kiosk 1', ST_GeomFromText('POLYGON((85 30, 95 30, 95 35, 85 35, 85 30))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "otherarea_map" VALUES (v_id, v_map_id);

        INSERT INTO "otherarea" (type, is_public, is_active, description, shape) VALUES (
            3, TRUE, TRUE, 'Kiosk 2', ST_GeomFromText('POLYGON((105 30, 115 30, 115 35, 105 35, 105 30))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "otherarea_map" VALUES (v_id, v_map_id);

        INSERT INTO "otherarea" (type, is_public, is_active, description, shape) VALUES (
            3, TRUE, TRUE, 'Vending Area A', ST_GeomFromText('POLYGON((30 80, 40 80, 40 85, 30 85, 30 80))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "otherarea_map" VALUES (v_id, v_map_id);

        INSERT INTO "otherarea" (type, is_public, is_active, description, shape) VALUES (
            3, TRUE, TRUE, 'Vending Area B', ST_GeomFromText('POLYGON((160 80, 170 80, 170 85, 160 85, 160 80))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "otherarea_map" VALUES (v_id, v_map_id);

        INSERT INTO "otherarea" (type, is_public, is_active, description, shape) VALUES (
            3, TRUE, TRUE, 'Seating Area A', ST_GeomFromText('POLYGON((60 130, 70 130, 70 140, 60 140, 60 130))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "otherarea_map" VALUES (v_id, v_map_id);

        INSERT INTO "otherarea" (type, is_public, is_active, description, shape) VALUES (
            3, TRUE, TRUE, 'Seating Area B', ST_GeomFromText('POLYGON((130 130, 140 130, 140 140, 130 140, 130 130))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "otherarea_map" VALUES (v_id, v_map_id);

        -- 12. The Main Corridor (Connecting everything)
        -- A complex MultiPolygon filling the space between store blocks
        v_corridor_geom := 'MULTIPOLYGON(((80 10, 120 10, 120 140, 80 140, 80 10)), ((10 60, 190 60, 190 90, 10 90, 10 60)))';
        INSERT INTO "otherarea" (type, is_public, is_active, description, shape) VALUES (
            0, TRUE, TRUE, 'Main Corridor Network', ST_GeomFromText(v_corridor_geom, 2385)
        ) RETURNING id INTO v_id; INSERT INTO "otherarea_map" VALUES (v_id, v_map_id);


        -- --- EVENT AREAS (6 Count) ---
        
        -- 1. Center Atrium (Main Event Space)
        INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape) VALUES (
            'Mall Ops', '02-1234', 3, TRUE, 'Main Atrium',
            ST_GeomFromText('POLYGON((90 65, 110 65, 110 85, 90 85, 90 65))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "eventarea_map" VALUES (v_id, v_map_id);

        -- 2. Science Expo (Left Corridor)
        INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape) VALUES (
            'Sci Dept', '02-1234', 1, TRUE, 'Science Zone',
            ST_GeomFromText('POLYGON((30 65, 45 65, 45 85, 30 85, 30 65))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "eventarea_map" VALUES (v_id, v_map_id);

        -- 3. Art Gallery (Right Corridor)
        INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape) VALUES (
            'Art Dept', '02-1234', 2, TRUE, 'Art Zone',
            ST_GeomFromText('POLYGON((155 65, 170 65, 170 85, 155 85, 155 65))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "eventarea_map" VALUES (v_id, v_map_id);

        -- 4. Entrance Promo (Top Center)
        INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape) VALUES (
            'Sales', '02-1234', 1, TRUE, 'North Promo',
            ST_GeomFromText('POLYGON((95 15, 105 15, 105 25, 95 25, 95 15))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "eventarea_map" VALUES (v_id, v_map_id);

        -- 5. Food Court Pop-up (Bottom Center)
        INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape) VALUES (
            'Food Ops', '02-1234', 1, TRUE, 'Food Pop-up',
            ST_GeomFromText('POLYGON((90 120, 110 120, 110 135, 90 135, 90 120))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "eventarea_map" VALUES (v_id, v_map_id);

        -- 6. Maker Space (Near Tech)
        INSERT INTO "eventarea" (organizer_name, organizer_phone, type, is_active, description, shape) VALUES (
            'Tech Ops', '02-1234', 2, TRUE, 'Maker Space',
            ST_GeomFromText('POLYGON((125 50, 135 50, 135 60, 125 60, 125 50))', 2385)
        ) RETURNING id INTO v_id; INSERT INTO "eventarea_map" VALUES (v_id, v_map_id);


        -- --- FACILITIES (18 Count) ---
        
        -- Exits (3) - On edges
        INSERT INTO "facility" (type, is_active, description, location) VALUES 
        (2, TRUE, 'North Exit', ST_GeomFromText('POINT(100 5)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);

        INSERT INTO "facility" (type, is_active, description, location) VALUES 
        (2, TRUE, 'West Exit', ST_GeomFromText('POINT(5 75)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);

        INSERT INTO "facility" (type, is_active, description, location) VALUES 
        (2, TRUE, 'East Exit', ST_GeomFromText('POINT(195 75)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);

        -- Elevators (3) - In corners
        INSERT INTO "facility" (type, is_active, description, location) VALUES (0, TRUE, 'Elevator A', ST_GeomFromText('POINT(15 15)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);
        INSERT INTO "facility" (type, is_active, description, location) VALUES (0, TRUE, 'Elevator B', ST_GeomFromText('POINT(185 15)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);
        INSERT INTO "facility" (type, is_active, description, location) VALUES (0, TRUE, 'Elevator C', ST_GeomFromText('POINT(15 135)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);

        -- Escalators (2) - Central Corridor
        INSERT INTO "facility" (type, is_active, description, location) VALUES (0, TRUE, 'Escalator Up', ST_GeomFromText('POINT(95 50)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);
        INSERT INTO "facility" (type, is_active, description, location) VALUES (0, TRUE, 'Escalator Down', ST_GeomFromText('POINT(105 50)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);

        -- Restrooms Icons (2) - Match OtherArea locations
        INSERT INTO "facility" (type, is_active, description, location) VALUES (1, TRUE, 'WC North', ST_GeomFromText('POINT(10 25)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);
        INSERT INTO "facility" (type, is_active, description, location) VALUES (1, TRUE, 'WC South', ST_GeomFromText('POINT(190 135)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);

        -- Service Desks (2)
        INSERT INTO "facility" (type, is_active, description, location) VALUES (3, TRUE, 'Info Desk A', ST_GeomFromText('POINT(100 30)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);
        INSERT INTO "facility" (type, is_active, description, location) VALUES (3, TRUE, 'Info Desk B', ST_GeomFromText('POINT(100 110)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);

        -- Fire Extinguishers (6) - Distributed
        INSERT INTO "facility" (type, is_active, description, location) VALUES (1, TRUE, 'Fire Ext 1', ST_GeomFromText('POINT(40 50)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);
        INSERT INTO "facility" (type, is_active, description, location) VALUES (1, TRUE, 'Fire Ext 2', ST_GeomFromText('POINT(160 50)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);
        INSERT INTO "facility" (type, is_active, description, location) VALUES (1, TRUE, 'Fire Ext 3', ST_GeomFromText('POINT(40 100)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);
        INSERT INTO "facility" (type, is_active, description, location) VALUES (1, TRUE, 'Fire Ext 4', ST_GeomFromText('POINT(160 100)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);
        INSERT INTO "facility" (type, is_active, description, location) VALUES (1, TRUE, 'Fire Ext 5', ST_GeomFromText('POINT(100 10)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);
        INSERT INTO "facility" (type, is_active, description, location) VALUES (1, TRUE, 'Fire Ext 6', ST_GeomFromText('POINT(100 145)', 2385));
        INSERT INTO "facility_map" (facility_id, map_id) VALUES (currval('facility_id_seq'), v_map_id);

    END LOOP;

    -- 5. Events (Using v_map_id_floor1)
    INSERT INTO "event" (event_name, start_date, end_date, image_url, is_active, description)
    VALUES ('Grand Opening', NOW(), NOW() + INTERVAL '30 days', 'https://yauycf.top/root/images/event/opening.png', TRUE, 'Mall Grand Opening')
    RETURNING id INTO v_event_id;

    -- Associate with center atrium
    INSERT INTO "event_eventarea" (event_id, eventarea_id)
    SELECT v_event_id, e.id FROM "eventarea" e 
    JOIN "eventarea_map" em ON em.eventarea_id = e.id
    WHERE em.map_id = v_map_id_floor1 AND e.type = 3;

    -- Associate with Anchor Stores (Type 2 and 4)
    INSERT INTO "event_storearea" (event_id, storearea_id)
    SELECT v_event_id, s.id FROM "storearea" s
    JOIN "storearea_map" sm ON sm.storearea_id = s.id
    WHERE sm.map_id = v_map_id_floor1 AND (s.type = 2 OR s.type = 4);

END $$;

COMMIT;