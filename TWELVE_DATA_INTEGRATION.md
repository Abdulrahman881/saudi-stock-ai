# تكامل Twelve Data Pro+ مع مستشار الأسهم السعودية

## 📊 معلومات الاشتراك

### الباقة المختارة: **Pro** ($229/شهر سنوي)
- ✅ **1,597 API calls/دقيقة** + **1,500 WebSocket**
- ✅ **47 سوق إضافي** (يشمل السوق السعودي XSAU)
- ✅ **Real-time data** للسوق السعودي
- ✅ **Technical Indicators جاهزة** (50+ مؤشر)
- ✅ **WebSocket** للبث المباشر
- ✅ **Fundamentals** (بيانات الشركات)
- ✅ **Pre/post market data**
- ✅ **Batch requests** (جلب عدة أسهم دفعة واحدة)

### البدائل:
- **Ultra** ($999/شهر): All markets + أكثر من 10,000 API calls
- **Grow** ($79/شهر): 377 API calls + بيانات محدودة

---

## 🚀 خطوات التكامل

### 1. الاشتراك والحصول على API Key

```bash
# الموقع
https://twelvedata.com/pricing

# بعد الاشتراك:
1. اذهب إلى Dashboard: https://twelvedata.com/account
2. انسخ API Key
3. احفظه في متغير البيئة
```

---

### 2. تثبيت المكتبة

```bash
pip3 install twelvedata
```

---

### 3. مثال استخدام

#### **جلب البيانات Real-time:**

```python
from twelvedata import TDClient

# Initialize client
td = TDClient(apikey="YOUR_API_KEY")

# جلب سعر سهم أرامكو (Real-time)
ts = td.time_series(
    symbol="2222.SR",
    interval="1min",
    outputsize=100
)
df = ts.as_pandas()
print(df)
```

#### **جلب Technical Indicators جاهزة:**

```python
# RSI
rsi = td.time_series(
    symbol="2222.SR",
    interval="1day",
    outputsize=30
).with_rsi(time_period=14).as_pandas()

# MACD
macd = td.time_series(
    symbol="2222.SR",
    interval="1day",
    outputsize=30
).with_macd().as_pandas()

# Bollinger Bands
bbands = td.time_series(
    symbol="2222.SR",
    interval="1day",
    outputsize=30
).with_bbands(time_period=20).as_pandas()

# جميع المؤشرات دفعة واحدة
all_indicators = td.time_series(
    symbol="2222.SR",
    interval="1day",
    outputsize=100
).with_rsi().with_macd().with_bbands().with_ema().with_sma().as_pandas()
```

#### **Batch Request (جلب عدة أسهم دفعة واحدة):**

```python
# جلب 10 أسهم دفعة واحدة
symbols = ["2222.SR", "1120.SR", "2010.SR", "1211.SR", "2030.SR"]

ts = td.time_series(
    symbol=",".join(symbols),
    interval="1day",
    outputsize=1
)

data = ts.as_json()
```

#### **WebSocket (البث المباشر):**

```python
import asyncio
from twelvedata import TDClient

td = TDClient(apikey="YOUR_API_KEY")

async def on_event(event):
    print(event)  # طباعة البيانات الحية

# الاشتراك في البث المباشر
td.websocket(on_event=on_event).subscribe(["2222.SR", "1120.SR"])
asyncio.run(td.websocket().connect())
```

---

## 📝 التكامل مع النظام الحالي

### الملفات التي ستُحدّث:

1. **`backend/data/twelve_data_client.py`** (جديد):
   - وحدة للتعامل مع Twelve Data API
   - دوال لجلب البيانات Real-time
   - دوال لجلب Technical Indicators

2. **`backend/data/database.py`**:
   - إضافة دوال لحفظ البيانات Real-time

3. **`python_scripts/fetch_stock_data_twelvedata.py`** (جديد):
   - سكريبت لجلب البيانات من Twelve Data
   - استبدال Yahoo Finance

4. **`python_scripts/generate_recommendations_ml.py`**:
   - استخدام Technical Indicators الجاهزة من Twelve Data
   - تحسين دقة التوصيات

5. **`server/scheduler.ts`**:
   - تحديث الجدولة لاستخدام Twelve Data
   - جلب البيانات كل 5 دقائق (بدلاً من كل ساعة)

---

## 🎯 المزايا بعد التكامل

### قبل (Yahoo Finance):
- ❌ بيانات متأخرة (15-20 دقيقة)
- ❌ حساب Technical Indicators يدوياً
- ❌ جلب الأسهم واحد واحد (بطيء)
- ❌ لا يوجد WebSocket

### بعد (Twelve Data Pro):
- ✅ بيانات Real-time
- ✅ Technical Indicators جاهزة (50+ مؤشر)
- ✅ Batch requests (جلب 380 سهم دفعة واحدة)
- ✅ WebSocket للبث المباشر
- ✅ دقة أعلى في التوصيات
- ✅ مضاربة لحظية حقيقية

---

## 💰 التكلفة

| الباقة | السعر/شهر | السعر/سنة | التوفير |
|--------|----------|-----------|---------|
| **Pro (شهري)** | $229 | $2,748 | - |
| **Pro (سنوي)** | $190.83 | $2,290 | $458 (17%) |

**التوصية**: الاشتراك السنوي (توفير $458)

---

## 📋 الخطوات التالية

1. ✅ **اشترك في Twelve Data Pro** (Annual)
2. ✅ **احصل على API Key**
3. ✅ **أرسل API Key**
4. ✅ **سأقوم بالتكامل الكامل**
5. ✅ **اختبار النظام**
6. ✅ **إطلاق النظام الجديد**

---

## 🔗 روابط مهمة

- **التسعير**: https://twelvedata.com/pricing
- **التوثيق**: https://twelvedata.com/docs
- **Dashboard**: https://twelvedata.com/account
- **Python SDK**: https://github.com/twelvedata/twelvedata-python
- **WebSocket Docs**: https://twelvedata.com/docs#websocket

---

## ⚠️ ملاحظات مهمة

1. **API Key سري**: لا تشاركه مع أحد
2. **Rate Limits**: 1,597 calls/دقيقة (كافية لـ 380 سهم)
3. **WebSocket**: 1,500 اتصال متزامن
4. **السوق السعودي**: XSAU (Saudi Stock Exchange)
5. **رموز الأسهم**: استخدم `.SR` (مثال: 2222.SR)

---

**جاهز للتكامل بمجرد حصولك على API Key!** 🚀
