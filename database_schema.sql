-- Saudi Stock Advisor Database Schema

-- جدول الأسهم
CREATE TABLE IF NOT EXISTS stocks (
    symbol VARCHAR(10) PRIMARY KEY,
    nameAr VARCHAR(100),
    nameEn VARCHAR(100),
    sector VARCHAR(50),
    currentPrice DECIMAL(10,2),
    `change` DECIMAL(10,2),
    changePercent DECIMAL(10,2),
    isActive BOOLEAN DEFAULT 1,
    lastUpdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_sector (sector),
    INDEX idx_active (isActive)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- جدول الأسعار التاريخية
CREATE TABLE IF NOT EXISTS historicalDailyPrices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    UNIQUE KEY unique_symbol_date (symbol, date),
    INDEX idx_symbol (symbol),
    INDEX idx_date (date),
    FOREIGN KEY (symbol) REFERENCES stocks(symbol) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- جدول التوصيات
CREATE TABLE IF NOT EXISTS recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    type ENUM('buy', 'sell', 'hold') NOT NULL,
    entryPrice DECIMAL(10,2) NOT NULL,
    targetPrice DECIMAL(10,2) NOT NULL,
    stopLoss DECIMAL(10,2) NOT NULL,
    confidence DECIMAL(5,2),
    analysis TEXT,
    status VARCHAR(20) DEFAULT 'active',
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_status (status),
    INDEX idx_created (createdAt),
    FOREIGN KEY (symbol) REFERENCES stocks(symbol) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- جدول ملخص السوق
CREATE TABLE IF NOT EXISTS marketSummary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tasiIndex DECIMAL(10,2),
    tasiChange DECIMAL(10,2),
    tasiChangePercent DECIMAL(5,2),
    stocksUp INT DEFAULT 0,
    stocksDown INT DEFAULT 0,
    stocksUnchanged INT DEFAULT 0,
    totalRecommendations INT DEFAULT 0,
    lastUpdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
