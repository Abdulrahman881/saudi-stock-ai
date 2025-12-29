# 🚀 دليل النشر على السيرفر

## 📋 المتطلبات

- Ubuntu Server (EC2) في منطقة `eu-north-1`
- Python 3.11+
- MySQL Client
- Git

---

## 🔧 خطوات التثبيت

### 1. الاتصال بالسيرفر

```bash
ssh ubuntu@13.53.169.204
```

### 2. تحديث النظام

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git mysql-client
```

### 3. استنساخ المشروع

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/saudi-stock-ai.git
cd saudi-stock-ai
```

### 4. تثبيت المكتبات

```bash
pip3 install -r requirements.txt
```

### 5. إنشاء الجداول في قاعدة البيانات

```bash
mysql -h tradedb.c3o44s2iqqg8.eu-north-1.rds.amazonaws.com \
      -u admin \
      -p \
      saudi_stock_advisor < database_schema.sql
```

**أدخل كلمة المرور عند الطلب**

### 6. سحب البيانات

```bash
python3 python_scripts/fetch_stock_data.py
```

**النتيجة المتوقعة:**
- ✅ إضافة 80+ سهم
- ✅ جلب سنتين من البيانات التاريخية
- ⏱️ يستغرق 2-5 دقائق

### 7. تدريب النموذج

```bash
python3 python_scripts/train_model.py
```

**النتيجة المتوقعة:**
- ✅ تدريب Random Forest
- ✅ حفظ النموذج في `/tmp/stock_model.pkl`
- ✅ دقة 60-70%

### 8. تشغيل API

#### تشغيل مباشر (للاختبار)

```bash
python3 backend/main.py
```

#### تشغيل في الخلفية

```bash
nohup python3 backend/main.py > api.log 2>&1 &
```

#### التحقق من التشغيل

```bash
curl http://localhost:8000/api/health
```

**النتيجة المتوقعة:**
```json
{
  "status": "healthy",
  "database": "connected",
  "model": "loaded"
}
```

---

## 🔄 الجدولة التلقائية

### إضافة Cron Jobs

```bash
crontab -e
```

أضف السطور التالية:

```bash
# تحديث البيانات كل ساعة
0 * * * * cd /home/ubuntu/saudi-stock-ai && /usr/bin/python3 python_scripts/fetch_stock_data.py >> /home/ubuntu/cron.log 2>&1

# توليد توصيات يومياً (8 صباحاً)
0 8 * * * /usr/bin/curl -X POST http://localhost:8000/api/recommendations/generate?limit=50

# إعادة تدريب النموذج أسبوعياً (السبت 2 صباحاً)
0 2 * * 6 cd /home/ubuntu/saudi-stock-ai && /usr/bin/python3 python_scripts/train_model.py >> /home/ubuntu/train.log 2>&1
```

---

## 🌐 فتح الـ API للعالم الخارجي

### تعديل Security Group في AWS

1. اذهب إلى **EC2 Console**
2. اختر **Security Groups**
3. اختر Security Group الخاص بالسيرفر
4. **Edit inbound rules**
5. أضف قاعدة:
   - **Type**: Custom TCP
   - **Port**: 8000
   - **Source**: 0.0.0.0/0 (أو IP محدد)
6. **Save rules**

### الوصول للـ API

```bash
# من أي مكان
curl http://13.53.169.204:8000/api/health

# Swagger Docs
http://13.53.169.204:8000/docs
```

---

## 🔍 استكشاف الأخطاء

### التحقق من حالة API

```bash
ps aux | grep python3
```

### عرض اللوجات

```bash
tail -f api.log
```

### إيقاف API

```bash
# البحث عن Process ID
ps aux | grep "backend/main.py"

# إيقاف العملية
kill <PID>
```

### إعادة تشغيل API

```bash
# إيقاف العملية القديمة
ps aux | grep "backend/main.py" | grep -v grep | awk '{print $2}' | xargs kill

# تشغيل جديد
sleep 2
nohup python3 backend/main.py > api.log 2>&1 &
```

---

## 📊 اختبار النظام

### 1. فحص الصحة

```bash
curl http://localhost:8000/api/health
```

### 2. جلب الأسهم

```bash
curl http://localhost:8000/api/stocks?limit=10
```

### 3. جلب التوصيات

```bash
curl http://localhost:8000/api/recommendations
```

### 4. توليد توصيات جديدة

```bash
curl -X POST "http://localhost:8000/api/recommendations/generate?limit=20"
```

---

## 🔐 الأمان

### تأمين قاعدة البيانات

- ✅ استخدم كلمة مرور قوية
- ✅ قيّد الوصول في Security Group
- ✅ فعّل SSL للاتصال

### تأمين API

- ✅ استخدم HTTPS (مع Nginx)
- ✅ أضف Authentication
- ✅ قيّد Rate Limiting

---

## 📝 ملاحظات

- ✅ السيرفر يجب أن يكون في نفس Region مع RDS (eu-north-1)
- ✅ Security Group يجب أن يسمح بالاتصال بين EC2 و RDS
- ✅ Port 8000 يجب أن يكون مفتوحاً للوصول الخارجي

---

## 🆘 الدعم

إذا واجهت أي مشاكل:
1. تحقق من اللوجات: `tail -f api.log`
2. تحقق من الاتصال بقاعدة البيانات
3. تحقق من Security Groups

---

**🎉 بالتوفيق!**
