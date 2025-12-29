# 🚀 Saudi Stock AI Advisor

مستشار ذكي للأسهم السعودية باستخدام التعلم الآلي (Machine Learning)

## 📋 المحتويات

- [نظرة عامة](#نظرة-عامة)
- [المزايا](#المزايا)
- [التقنيات المستخدمة](#التقنيات-المستخدمة)
- [التثبيت](#التثبيت)
- [الاستخدام](#الاستخدام)
- [API Endpoints](#api-endpoints)
- [قاعدة البيانات](#قاعدة-البيانات)

---

## 🎯 نظرة عامة

نظام ذكي يوفر توصيات تداول يومية للأسهم السعودية باستخدام:
- **Machine Learning** (Random Forest)
- **Technical Indicators** (RSI, MACD, Bollinger Bands, ATR)
- **Yahoo Finance API** لجلب البيانات

---

## ✨ المزايا

- ✅ **توصيات ذكية**: Buy/Sell/Hold مع نسبة ثقة
- ✅ **نقاط دخول وخروج**: Entry Price, Target Price, Stop Loss
- ✅ **تغطية شاملة**: 80+ سهم سعودي
- ✅ **تحديث تلقائي**: جلب البيانات من Yahoo Finance
- ✅ **RESTful API**: FastAPI مع توثيق تلقائي
- ✅ **قاعدة بيانات**: MySQL (AWS RDS)

---

## 🛠️ التقنيات المستخدمة

### Backend
- **FastAPI** - Web Framework
- **Python 3.11+**
- **MySQL** - Database
- **scikit-learn** - Machine Learning
- **pandas & numpy** - Data Processing
- **yfinance** - Stock Data

### Machine Learning
- **Random Forest Classifier**
- **Technical Indicators**: RSI, MACD, SMA, EMA, Bollinger Bands, ATR
- **Features**: 12 مؤشر فني

---

## 📦 التثبيت

### المتطلبات
- Python 3.11+
- MySQL Database (AWS RDS)
- pip3

### 1. استنساخ المشروع

```bash
git clone https://github.com/YOUR_USERNAME/saudi-stock-ai.git
cd saudi-stock-ai
```

### 2. تثبيت المكتبات

```bash
pip3 install -r requirements.txt
```

### 3. إعداد قاعدة البيانات

تأكد من:
- ✅ قاعدة البيانات MySQL تعمل
- ✅ Security Group يسمح بالاتصال
- ✅ بيانات الاتصال صحيحة في `backend/data/database.py`

```python
# backend/data/database.py
self.host = "tradedb.c3o44s2iqqg8.eu-north-1.rds.amazonaws.com"
self.user = "admin"
self.password = "YOUR_PASSWORD"
self.database = "saudi_stock_advisor"
```

### 4. إنشاء الجداول

```sql
-- جدول الأسهم
CREATE TABLE stocks (
    symbol VARCHAR(10) PRIMARY KEY,
    nameAr VARCHAR(100),
    nameEn VARCHAR(100),
    sector VARCHAR(50),
    currentPrice DECIMAL(10,2),
    `change` DECIMAL(10,2),
    changePercent DECIMAL(10,2),
    isActive BOOLEAN DEFAULT 1,
    lastUpdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول الأسعار التاريخية
CREATE TABLE historicalDailyPrices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10),
    date DATE,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    UNIQUE KEY unique_symbol_date (symbol, date),
    FOREIGN KEY (symbol) REFERENCES stocks(symbol)
);

-- جدول التوصيات
CREATE TABLE recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10),
    type ENUM('buy', 'sell', 'hold'),
    entryPrice DECIMAL(10,2),
    targetPrice DECIMAL(10,2),
    stopLoss DECIMAL(10,2),
    confidence DECIMAL(5,2),
    analysis TEXT,
    status VARCHAR(20) DEFAULT 'active',
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (symbol) REFERENCES stocks(symbol)
);

-- جدول ملخص السوق
CREATE TABLE marketSummary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tasiIndex DECIMAL(10,2),
    tasiChange DECIMAL(10,2),
    tasiChangePercent DECIMAL(5,2),
    stocksUp INT,
    stocksDown INT,
    stocksUnchanged INT,
    totalRecommendations INT,
    lastUpdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚀 الاستخدام

### 1. سحب البيانات من Yahoo Finance

```bash
python3 python_scripts/fetch_stock_data.py
```

**النتيجة:**
- إضافة 80+ سهم إلى قاعدة البيانات
- جلب آخر سنتين من البيانات التاريخية
- تحديث الأسعار الحالية

### 2. تدريب نموذج ML

```bash
python3 python_scripts/train_model.py
```

**النتيجة:**
- تدريب Random Forest على البيانات التاريخية
- حفظ النموذج في `/tmp/stock_model.pkl`
- عرض دقة النموذج والمقاييس

### 3. تشغيل FastAPI Server

```bash
cd backend
python3 main.py
```

**أو باستخدام uvicorn:**

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**أو في الخلفية:**

```bash
nohup python3 backend/main.py > api.log 2>&1 &
```

### 4. الوصول للـ API

- **API**: http://YOUR_SERVER_IP:8000
- **Docs**: http://YOUR_SERVER_IP:8000/docs
- **Health**: http://YOUR_SERVER_IP:8000/api/health

---

## 📡 API Endpoints

### Health Check
```bash
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "model": "loaded",
  "timestamp": "2025-12-29T10:00:00"
}
```

### Get Stocks
```bash
GET /api/stocks?limit=100&sector=البنوك
```

**Response:**
```json
{
  "count": 10,
  "stocks": [
    {
      "symbol": "1120",
      "nameAr": "الراجحي",
      "nameEn": "Al Rajhi Bank",
      "sector": "البنوك",
      "currentPrice": 95.50,
      "change": 1.20,
      "changePercent": 1.27
    }
  ]
}
```

### Get Stock Details
```bash
GET /api/stocks/1120
```

**Response:**
```json
{
  "stock": {...},
  "history": [...]
}
```

### Get Recommendations
```bash
GET /api/recommendations?limit=50
```

**Response:**
```json
{
  "count": 20,
  "recommendations": [
    {
      "symbol": "1120",
      "nameAr": "الراجحي",
      "type": "buy",
      "entryPrice": 93.59,
      "targetPrice": 100.28,
      "stopLoss": 92.62,
      "confidence": 78.50,
      "analysis": "RSI: 45.2, MACD: 0.85",
      "createdAt": "2025-12-29 08:00:00"
    }
  ]
}
```

### Generate Recommendations
```bash
POST /api/recommendations/generate?limit=20
```

**Response:**
```json
{
  "generated": 18,
  "total_stocks": 20,
  "errors": []
}
```

### Market Summary
```bash
GET /api/market-summary
```

### Get Sectors
```bash
GET /api/sectors
```

---

## 🗄️ قاعدة البيانات

### الاتصال

```python
from backend.data.database import Database

db = Database()
stocks = db.get_all_stocks()
db.close()
```

### الدوال المتاحة

```python
# الأسهم
db.get_all_stocks()
db.get_stock_by_symbol(symbol)
db.insert_stock(symbol, name_ar, name_en, sector)
db.update_stock_price(symbol, price, change, change_percent)

# البيانات التاريخية
db.insert_historical_price(symbol, date, open, high, low, close, volume)
db.get_historical_prices(symbol, limit=100)
db.get_all_historical_data(days=500)

# التوصيات
db.insert_recommendation(symbol, type, entry_price, target_price, stop_loss, confidence, analysis)
db.get_active_recommendations(limit=50)
db.delete_old_recommendations(days=7)
```

---

## 📊 هيكل المشروع

```
saudi-stock-ai/
├── backend/
│   ├── data/
│   │   └── database.py          # وحدة قاعدة البيانات
│   ├── models/
│   │   └── ml_model.py          # نموذج ML
│   └── main.py                  # FastAPI Application
├── python_scripts/
│   ├── saudi_stocks_list.py     # قائمة الأسهم
│   ├── fetch_stock_data.py      # سحب البيانات
│   └── train_model.py           # تدريب النموذج
├── requirements.txt             # المكتبات المطلوبة
└── README.md                    # هذا الملف
```

---

## 🔄 الجدولة التلقائية (Cron)

لتشغيل السكريبتات تلقائياً:

```bash
crontab -e
```

أضف:

```bash
# تحديث البيانات كل ساعة
0 * * * * cd /home/ubuntu/projects/saudi-stock-ai && python3 python_scripts/fetch_stock_data.py

# توليد توصيات يومياً (8 صباحاً)
0 8 * * * curl -X POST http://localhost:8000/api/recommendations/generate?limit=50

# إعادة تدريب النموذج أسبوعياً (السبت 2 صباحاً)
0 2 * * 6 cd /home/ubuntu/projects/saudi-stock-ai && python3 python_scripts/train_model.py
```

---

## 🐛 استكشاف الأخطاء

### خطأ في الاتصال بقاعدة البيانات

```bash
# تحقق من Security Group
# تأكد أن Port 3306 مفتوح لـ IP السيرفر

# اختبار الاتصال
telnet tradedb.c3o44s2iqqg8.eu-north-1.rds.amazonaws.com 3306
```

### النموذج غير محمّل

```bash
# تدريب النموذج
python3 python_scripts/train_model.py

# التحقق من وجود الملف
ls -lh /tmp/stock_model.pkl
```

---

## 📝 ملاحظات

- ✅ البيانات من Yahoo Finance (مجاني، متأخر 15-20 دقيقة)
- ✅ مناسب للتوصيات اليومية
- ⚠️ للمضاربة اللحظية، تحتاج Real-time API (Tadawul API)

---

## 📧 التواصل

لأي استفسارات أو مشاكل، افتح Issue على GitHub

---

## 📄 الترخيص

MIT License

---

**🚀 بالتوفيق في التداول!**
