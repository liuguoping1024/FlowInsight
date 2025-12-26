-- ============================================
-- 用户功能相关表
-- ============================================

USE flowinsight;

-- 用户持股表
CREATE TABLE IF NOT EXISTS holdings (
    holding_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '持股ID',
    user_id INT NOT NULL COMMENT '用户ID',
    stock_id INT NOT NULL COMMENT '股票ID',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码（冗余字段，便于查询）',
    cost_price DECIMAL(10,3) NOT NULL COMMENT '成本价',
    quantity INT NOT NULL COMMENT '持股数量（股）',
    buy_date DATE COMMENT '买入日期',
    notes TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_stock_id (stock_id),
    INDEX idx_stock_code (stock_code),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户持股表';

-- 用户收藏表
CREATE TABLE IF NOT EXISTS watchlist (
    watch_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '收藏ID',
    user_id INT NOT NULL COMMENT '用户ID',
    stock_id INT NOT NULL COMMENT '股票ID',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码（冗余字段，便于查询）',
    notes TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    UNIQUE KEY uk_user_stock (user_id, stock_code),
    INDEX idx_user_id (user_id),
    INDEX idx_stock_id (stock_id),
    INDEX idx_stock_code (stock_code),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户收藏表';

