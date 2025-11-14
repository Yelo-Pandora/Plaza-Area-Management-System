-- 启用 PostGIS 扩展
CREATE EXTENSION IF NOT EXISTS postgis;

-- 实体集:
CREATE TABLE admin (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    account VARCHAR(64) UNIQUE NOT NULL,
    password VARCHAR(256) NOT NULL,
    name VARCHAR(64)
);

CREATE TABLE building (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(64) UNIQUE NOT NULL,
    address VARCHAR(256) NOT NULL,
    description VARCHAR(256)
);

CREATE TABLE map (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    building_id INTEGER REFERENCES building(id) NOT NULL,
    floor_number INTEGER NOT NULL,
    detail geometry(GEOMETRYCOLLECTION,2385) NOT NULL,-- SRID的值为2385,适合上海的单位为米的二维坐标系(X,Y),X方向为北,Y方向为东 https://epsg.io/2385
    UNIQUE (building_id, floor_number)
);

CREATE TABLE facility (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    is_active BOOLEAN DEFAULT TRUE,
    location geometry(POINT,2385) NOT NULL,-- SRID的值为2385
    description VARCHAR(256),
    type INTEGER NOT NULL-- 一个整数对应一个确定的种类(电梯、垃圾桶、按摩椅...)
);

CREATE TABLE storearea(
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    is_active BOOLEAN DEFAULT TRUE,
    shape geometry(POLYGON,2385) NOT NULL,-- SRID的值为2385
    description VARCHAR(256),
    -- 以下为特有属性
    store_name VARCHAR(64) NOT NULL,-- 店铺名称
    owner_name VARCHAR(64) NOT NULL,-- 租户名称
    owner_phone VARCHAR(16) NOT NULL,-- 租户的联系电话
    logo_url VARCHAR(256),
    open_time TIME DEFAULT '00:00:00',--营业的起始时间
    close_time TIME DEFAULT '23:59:59',--营业的结束时间
    type INTEGER DEFAULT 0,-- 一个整数对应一个确定的种类(店铺种类: 美食、影视、服装、游戏...其他:0)
    api_url VARCHAR(256)-- 预留的API跳转接口,该点作为预留扩展功能
);

CREATE TABLE eventarea(
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    is_active BOOLEAN DEFAULT TRUE,
    shape geometry(POLYGON,2385) NOT NULL,-- SRID的值为2385
    description VARCHAR(256),
    -- 以下为特有属性
    organizer_name VARCHAR(64) NOT NULL,-- 场地活动负责人的名称
    organizer_phone VARCHAR(16) NOT NULL,-- 场地活动负责人的联系电话
    type INTEGER DEFAULT 0-- 一个整数对应一个确定的种类(场地活动的种类: 音乐、影视、游戏...其他:0)
);

CREATE TABLE otherarea(
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    is_active BOOLEAN DEFAULT TRUE,
    shape geometry(POLYGON,2385) NOT NULL,-- SRID的值为2385
    description VARCHAR(256),
    -- 以下为特有属性
    type INTEGER NOT NULL,-- 一个整数对应一个确定的种类(卫生间、茶水间、母婴室、休息室、自习室...)
    is_public BOOLEAN DEFAULT TRUE-- 该属性只有在is_active==TRUE时才有意义(is_public==TRUE多人公开使用的,is_public==FALSE私人预约使用的),该点作为预留扩展功能
);

CREATE TABLE event (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    is_active BOOLEAN DEFAULT TRUE,
    description VARCHAR(256),
    event_name VARCHAR(64) NOT NULL,
    start_date TIMESTAMP NOT NULL,-- 活动的起始日期时间
    end_date TIMESTAMP NOT NULL,-- 活动的结束日期时间
    image_url VARCHAR(256)
);

-- 联系集:
CREATE TABLE facility_map(
    facility_id INTEGER REFERENCES facility(id),
    map_id INTEGER REFERENCES map(id),
    PRIMARY KEY(facility_id, map_id)
);

CREATE TABLE storearea_map(
    storearea_id INTEGER REFERENCES storearea(id),
    map_id INTEGER REFERENCES map(id),
    PRIMARY KEY(storearea_id, map_id)
);

CREATE TABLE otherarea_map(
    otherarea_id INTEGER REFERENCES otherarea(id),
    map_id INTEGER REFERENCES map(id),
    PRIMARY KEY(otherarea_id, map_id)
);

CREATE TABLE eventarea_map(
    eventarea_id INTEGER REFERENCES eventarea(id),
    map_id INTEGER REFERENCES map(id),
    PRIMARY KEY(eventarea_id, map_id)
);

CREATE TABLE event_storearea(
    event_id INTEGER REFERENCES event(id),
    storearea_id INTEGER REFERENCES storearea(id),
    PRIMARY KEY(event_id, storearea_id)
);

CREATE TABLE event_eventarea(
    event_id INTEGER REFERENCES event(id),
    eventarea_id INTEGER REFERENCES eventarea(id),
    PRIMARY KEY(event_id, eventarea_id)
);

-- 索引:
CREATE INDEX idx_map_detail 
    ON map 
    USING GIST(detail);

CREATE INDEX idx_facility_location 
    ON facility
    USING GIST(location);

CREATE INDEX idx_storearea_shape 
    ON storearea 
    USING GIST(shape);

CREATE INDEX idx_eventarea_shape 
    ON eventarea
    USING GIST(shape);

CREATE INDEX idx_otherarea_shape 
    ON otherarea 
    USING GIST(shape);