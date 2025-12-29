-- إضافة جدول تقييم أداء الصفقات

USE saudi_stock_advisor;

-- جدول أداء الصفقات
CREATE TABLE IF NOT EXISTS trade_performance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recommendation_id INT NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    entry_price DECIMAL(10,2) NOT NULL,
    target_price DECIMAL(10,2) NOT NULL,
    stop_loss DECIMAL(10,2) NOT NULL,
    exit_price DECIMAL(10,2),
    entry_date TIMESTAMP NOT NULL,
    exit_date TIMESTAMP,
    status ENUM('open', 'target_hit', 'stop_loss_hit', 'closed_neutral') DEFAULT 'open',
    profit_loss DECIMAL(10,2),
    profit_loss_percent DECIMAL(5,2),
    high_during_trade DECIMAL(10,2),
    low_during_trade DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY idx_symbol (symbol),
    KEY idx_status (status),
    KEY idx_entry_date (entry_date),
    KEY idx_recommendation_id (recommendation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- تحديث جدول recommendations لإضافة حقل trade_performance_id
ALTER TABLE recommendations 
ADD COLUMN trade_performance_id INT,
ADD COLUMN is_evaluated BOOLEAN DEFAULT 0,
ADD COLUMN evaluation_date TIMESTAMP NULL;

-- جدول إحصائيات الأداء اليومية
CREATE TABLE IF NOT EXISTS daily_performance_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_trades INT DEFAULT 0,
    successful_trades INT DEFAULT 0,
    failed_trades INT DEFAULT 0,
    neutral_trades INT DEFAULT 0,
    success_rate DECIMAL(5,2),
    avg_profit DECIMAL(10,2),
    avg_loss DECIMAL(10,2),
    total_profit_loss DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SELECT 'Trade performance tables created successfully!' as status;
