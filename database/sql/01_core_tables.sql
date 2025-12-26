-- ============================================
-- 资金流向监控分析系统 - 核心表结构
-- 数据库: MariaDB 10.11+
-- 创建时间: 2025-01-XX
-- ============================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS flowinsight CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE flowinsight;

-- ============================================
-- 一、用户权限模块
-- ============================================

-- 1. 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希值',
    email VARCHAR(100) UNIQUE COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    real_name VARCHAR(50) COMMENT '真实姓名',
    avatar_url VARCHAR(255) COMMENT '头像URL',
    status VARCHAR(20) DEFAULT 'active' COMMENT '账户状态: active-激活, disabled-禁用, locked-锁定',
    last_login_at TIMESTAMP NULL COMMENT '最后登录时间',
    last_login_ip VARCHAR(50) COMMENT '最后登录IP',
    login_count INT DEFAULT 0 COMMENT '登录次数统计',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by INT COMMENT '创建者用户ID',
    remarks TEXT COMMENT '备注信息',
    
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 2. 用户组表
CREATE TABLE IF NOT EXISTS user_groups (
    group_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '组ID',
    group_code VARCHAR(50) UNIQUE NOT NULL COMMENT '组代码: user, admin',
    group_name VARCHAR(100) NOT NULL COMMENT '组名称',
    group_level INT DEFAULT 1 COMMENT '组级别: 1-普通用户, 99-管理员',
    permissions JSON COMMENT '权限列表,JSON格式',
    description TEXT COMMENT '组描述',
    is_system BOOLEAN DEFAULT FALSE COMMENT '是否系统组',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active-启用, disabled-禁用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_group_level (group_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户组表';

-- 插入默认用户组
INSERT INTO user_groups (group_code, group_name, group_level, permissions, description, is_system, status) VALUES
('user', '普通用户', 1, 
 '{"stock_view": true, "holding_manage": true, "watchlist_manage": true, "alert_receive": true, "stock_export": false, "user_manage": false, "data_manage": false, "system_config": false, "task_manage": false}',
 '系统普通用户组', TRUE, 'active'),
('admin', '管理员', 99,
 '{"stock_view": true, "stock_export": true, "holding_manage": true, "watchlist_manage": true, "alert_receive": true, "user_manage": true, "data_manage": true, "system_config": true, "task_manage": true}',
 '系统管理员组', TRUE, 'active')
ON DUPLICATE KEY UPDATE group_name=VALUES(group_name);

-- 3. 用户组关系表
CREATE TABLE IF NOT EXISTS user_group_relations (
    relation_id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '关系ID',
    user_id INT NOT NULL COMMENT '用户ID',
    group_id INT NOT NULL COMMENT '组ID',
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '分配时间',
    assigned_by INT COMMENT '分配操作者ID',
    expires_at TIMESTAMP NULL COMMENT '过期时间',
    status VARCHAR(20) DEFAULT 'active' COMMENT '关系状态: active-有效, expired-已过期',
    
    UNIQUE KEY uk_user_group (user_id, group_id),
    INDEX idx_user_id (user_id),
    INDEX idx_group_id (group_id),
    INDEX idx_expires_at (expires_at),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES user_groups(group_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户组关系表';

-- ============================================
-- 二、股票基础数据模块
-- ============================================

-- 4. 股票基础信息表
CREATE TABLE IF NOT EXISTS stocks (
    stock_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '股票ID',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    stock_name VARCHAR(50) NOT NULL COMMENT '股票名称',
    exchange VARCHAR(10) NOT NULL COMMENT '交易所: SH-上海, SZ-深圳',
    market_code VARCHAR(5) NOT NULL COMMENT '市场代码: 1-沪市, 0-深市',
    secid VARCHAR(20) UNIQUE NOT NULL COMMENT '东财证券ID: 1.600118',
    industry VARCHAR(50) COMMENT '所属行业',
    industry_code VARCHAR(20) COMMENT '行业代码',
    concept TEXT COMMENT '所属概念,多个概念逗号分隔',
    area VARCHAR(50) COMMENT '所属地区',
    market_cap DECIMAL(20,2) COMMENT '总市值,单位:元',
    circulation_cap DECIMAL(20,2) COMMENT '流通市值,单位:元',
    total_shares BIGINT COMMENT '总股本,单位:股',
    circulation_shares BIGINT COMMENT '流通股本,单位:股',
    listing_date DATE COMMENT '上市日期',
    pe_ratio DECIMAL(10,4) COMMENT '市盈率-动态',
    pb_ratio DECIMAL(10,4) COMMENT '市净率',
    status VARCHAR(20) DEFAULT 'normal' COMMENT '状态: normal-正常, suspended-停牌, delisted-退市',
    is_st BOOLEAN DEFAULT FALSE COMMENT '是否ST股',
    is_star BOOLEAN DEFAULT FALSE COMMENT '是否科创板',
    is_gem BOOLEAN DEFAULT FALSE COMMENT '是否创业板',
    last_sync_at TIMESTAMP NULL COMMENT '最后同步时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    remarks TEXT COMMENT '备注',
    
    UNIQUE KEY uk_code_exchange (stock_code, exchange),
    INDEX idx_stock_code (stock_code),
    INDEX idx_stock_name (stock_name),
    INDEX idx_industry (industry),
    INDEX idx_exchange (exchange),
    INDEX idx_status (status),
    INDEX idx_listing_date (listing_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='股票基础信息表';

-- 5. 板块信息表
CREATE TABLE IF NOT EXISTS sectors (
    sector_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '板块ID',
    sector_code VARCHAR(20) UNIQUE NOT NULL COMMENT '板块代码',
    sector_name VARCHAR(100) NOT NULL COMMENT '板块名称',
    sector_type VARCHAR(20) NOT NULL COMMENT '板块类型: industry-行业, concept-概念, area-地域',
    parent_sector_id INT COMMENT '父板块ID',
    stock_count INT DEFAULT 0 COMMENT '包含股票数量',
    stock_codes TEXT COMMENT '包含的股票代码列表,逗号分隔',
    leading_stocks JSON COMMENT '龙头股信息,JSON数组',
    description TEXT COMMENT '板块描述',
    hot_rank INT COMMENT '热度排名',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active-活跃, inactive-不活跃',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_sector_name (sector_name),
    INDEX idx_sector_type (sector_type),
    INDEX idx_parent_sector (parent_sector_id),
    INDEX idx_hot_rank (hot_rank),
    INDEX idx_status (status),
    FOREIGN KEY (parent_sector_id) REFERENCES sectors(sector_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='板块信息表';

-- ============================================
-- 三、资金流向数据模块（核心）
-- ============================================

-- 6. 资金流向数据表（核心表）
CREATE TABLE IF NOT EXISTS capital_flow (
    flow_id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '流向ID',
    stock_id INT NOT NULL COMMENT '股票ID',
    trade_date DATE NOT NULL COMMENT '交易日期',
    
    -- 主力资金数据
    main_inflow DECIMAL(15,2) COMMENT '主力净流入,单位:元',
    main_inflow_rate DECIMAL(8,4) COMMENT '主力净流入占比,单位:%',
    
    -- 超大单数据(>100万)
    super_inflow DECIMAL(15,2) COMMENT '超大单净流入,单位:元',
    super_inflow_rate DECIMAL(8,4) COMMENT '超大单净流入占比,单位:%',
    
    -- 大单数据(20-100万)
    large_inflow DECIMAL(15,2) COMMENT '大单净流入,单位:元',
    large_inflow_rate DECIMAL(8,4) COMMENT '大单净流入占比,单位:%',
    
    -- 中单数据(5-20万)
    medium_inflow DECIMAL(15,2) COMMENT '中单净流入,单位:元',
    medium_inflow_rate DECIMAL(8,4) COMMENT '中单净流入占比,单位:%',
    
    -- 小单数据(<5万)
    small_inflow DECIMAL(15,2) COMMENT '小单净流入,单位:元',
    small_inflow_rate DECIMAL(8,4) COMMENT '小单净流入占比,单位:%',
    
    -- 价格数据
    open_price DECIMAL(10,3) COMMENT '开盘价',
    high_price DECIMAL(10,3) COMMENT '最高价',
    low_price DECIMAL(10,3) COMMENT '最低价',
    close_price DECIMAL(10,3) COMMENT '收盘价',
    pre_close_price DECIMAL(10,3) COMMENT '昨收价',
    change_amount DECIMAL(10,3) COMMENT '涨跌额',
    change_percent DECIMAL(8,4) COMMENT '涨跌幅,单位:%',
    
    -- 成交数据
    volume BIGINT COMMENT '成交量,单位:股',
    amount DECIMAL(20,2) COMMENT '成交额,单位:元',
    turnover_rate DECIMAL(8,4) COMMENT '换手率,单位:%',
    volume_ratio DECIMAL(10,4) COMMENT '量比',
    amplitude DECIMAL(8,4) COMMENT '振幅,单位:%',
    
    -- 元数据
    data_source VARCHAR(50) DEFAULT 'eastmoney' COMMENT '数据来源',
    is_valid BOOLEAN DEFAULT TRUE COMMENT '数据是否有效',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    UNIQUE KEY uk_stock_date (stock_id, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_main_inflow (main_inflow),
    INDEX idx_main_inflow_rate (main_inflow_rate),
    INDEX idx_super_inflow (super_inflow),
    INDEX idx_change_percent (change_percent),
    INDEX idx_amount (amount),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='资金流向数据表';

-- ============================================
-- 四、系统配置模块
-- ============================================

-- 系统配置表（用于频率控制等配置）
CREATE TABLE IF NOT EXISTS system_config (
    config_key VARCHAR(100) PRIMARY KEY COMMENT '配置键',
    config_value VARCHAR(255) NOT NULL COMMENT '配置值',
    config_type VARCHAR(50) NOT NULL COMMENT '配置类型: int, float, string, json',
    description TEXT COMMENT '配置说明',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- 插入默认配置
INSERT INTO system_config (config_key, config_value, config_type, description) VALUES
('api_request_interval', '1', 'float', 'API请求间隔（秒）'),
('market_collection_interval', '300', 'int', '全市场采集间隔（秒，5分钟）'),
('user_stock_interval', '60', 'int', '用户股票监控间隔（秒，1分钟）'),
('sector_collection_interval', '600', 'int', '板块采集间隔（秒，10分钟）'),
('limit_up_monitor_interval', '60', 'int', '涨跌停监控间隔（秒，1分钟）'),
('max_concurrent_requests', '5', 'int', '最大并发请求数'),
('retry_max_attempts', '3', 'int', '失败重试最大次数'),
('retry_delay', '2', 'int', '重试延迟（秒）'),
('data_collection_time', '18:00:00', 'string', '交易日收盘后数据采集时间')
ON DUPLICATE KEY UPDATE config_value=VALUES(config_value);

