# 🚀 تحديث السيرفر

## 📋 الخطوات:

### 1. الاتصال بالسيرفر:
```bash
ssh -i ~/Downloads/saudi-stock-advisor-key.pem ubuntu@13.53.169.204
```

### 2. سحب التحديثات من GitHub:
```bash
cd ~/saudi-stock-ai
git pull origin master
```

### 3. إضافة الجداول الجديدة:
```bash
mysql -h tradedb.c3o44s2iqqg8.eu-north-1.rds.amazonaws.com -u admin -p0537681225 << 'EOF'
USE saudi_stock_advisor;

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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SHOW TABLES;
EOF
```

### 4. إضافة أعمدة جديدة لجدول recommendations:
```bash
mysql -h tradedb.c3o44s2iqqg8.eu-north-1.rds.amazonaws.com -u admin -p0537681225 -e "
USE saudi_stock_advisor;
ALTER TABLE recommendations ADD COLUMN trade_performance_id INT;
ALTER TABLE recommendations ADD COLUMN is_evaluated BOOLEAN DEFAULT 0;
ALTER TABLE recommendations ADD COLUMN evaluation_date TIMESTAMP NULL;
" 2>/dev/null || echo "Columns may already exist"
```

### 5. إعادة تشغيل API:
```bash
cd ~/saudi-stock-ai

# إيقاف API القديم
sudo pkill -9 -f "python3.*main.py"

# تشغيل API جديد
nohup python3 backend/main.py > api.log 2>&1 &

# انتظار 3 ثوانٍ
sleep 3

# اختبار
curl http://localhost:8000/api/health
```

### 6. إضافة Cron Job (تقييم يومي الساعة 5 عصراً):
```bash
# فتح crontab
crontab -e

# إضافة السطر التالي:
0 17 * * * cd /home/ubuntu/saudi-stock-ai && /usr/bin/python3 python_scripts/daily_evaluation.py >> /home/ubuntu/saudi-stock-ai/cron.log 2>&1
```

### 7. اختبار السكريبت اليومي (اختياري):
```bash
cd ~/saudi-stock-ai
python3 python_scripts/daily_evaluation.py
```

---

## 🌐 فتح Port 8000 للوصول الخارجي:

### في AWS Console:
1. **EC2** → **Security Groups**
2. اختر Security Group الخاص بـ `13.53.169.204`
3. **Edit inbound rules**
4. **Add rule:**
   - Type: Custom TCP
   - Port: 8000
   - Source: 0.0.0.0/0
5. **Save**

---

## ✅ التحقق من النظام:

### اختبار API:
```bash
# Health check
curl http://localhost:8000/api/health

# جلب الصفقات
curl http://localhost:8000/api/trades/history?limit=10

# جلب الإحصائيات
curl http://localhost:8000/api/trades/stats

# تقييم الصفقات (يدوي)
curl -X POST http://localhost:8000/api/trades/evaluate
```

### اختبار من الخارج:
```
http://13.53.169.204:8000/docs
http://13.53.169.204:8000/api/health
```

---

## 📊 مراقبة Cron Job:

```bash
# عرض آخر 50 سطر من اللوج
tail -50 ~/saudi-stock-ai/cron.log

# مراقبة اللوج مباشرة
tail -f ~/saudi-stock-ai/cron.log

# عرض جدول Cron
crontab -l
```

---

## 🔄 إعادة تشغيل كل شيء:

```bash
# إيقاف API
sudo pkill -9 -f "python3.*main.py"

# تشغيل API
cd ~/saudi-stock-ai
nohup python3 backend/main.py > api.log 2>&1 &

# اختبار
curl http://localhost:8000/api/health
```

---

## 📝 ملاحظات:

- ✅ Cron Job يعمل كل يوم الساعة 5 عصراً (17:00)
- ✅ يقيّم الصفقات القديمة
- ✅ يولّد توصيات جديدة
- ✅ يحفظ الإحصائيات
- ✅ اللوج في: `~/saudi-stock-ai/cron.log`
