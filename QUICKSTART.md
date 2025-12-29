# ⚡ دليل البدء السريع

## 🚀 على سيرفرك (13.53.169.204)

### 1. استنساخ المشروع

```bash
ssh ubuntu@13.53.169.204
cd ~
git clone https://github.com/YOUR_USERNAME/saudi-stock-ai.git
cd saudi-stock-ai
```

### 2. تثبيت المكتبات

```bash
pip3 install -r requirements.txt
```

### 3. إنشاء الجداول

```bash
mysql -h tradedb.c3o44s2iqqg8.eu-north-1.rds.amazonaws.com \
      -u admin \
      -p0537681225 \
      saudi_stock_advisor < database_schema.sql
```

### 4. سحب البيانات (2-5 دقائق)

```bash
python3 python_scripts/fetch_stock_data.py
```

### 5. تدريب النموذج (1-3 دقائق)

```bash
python3 python_scripts/train_model.py
```

### 6. تشغيل API

```bash
nohup python3 backend/main.py > api.log 2>&1 &
```

### 7. اختبار

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/stocks?limit=5
```

---

## 🌐 فتح للعالم الخارجي

### في AWS Console:

1. **EC2** → **Security Groups**
2. اختر Security Group الخاص بالسيرفر
3. **Edit inbound rules**
4. أضف:
   - Type: Custom TCP
   - Port: 8000
   - Source: 0.0.0.0/0
5. **Save**

### الوصول:

```bash
http://13.53.169.204:8000/docs
```

---

## 📋 الأوامر المفيدة

```bash
# فحص حالة API
ps aux | grep "backend/main.py"

# عرض اللوجات
tail -f api.log

# إعادة تشغيل API
ps aux | grep "backend/main.py" | awk '{print $2}' | xargs kill
nohup python3 backend/main.py > api.log 2>&1 &

# توليد توصيات
curl -X POST "http://localhost:8000/api/recommendations/generate?limit=50"
```

---

**✅ تم! API جاهز للاستخدام**
