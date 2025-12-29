#!/usr/bin/env python3
"""
تدريب نموذج Random Forest جديد للتوصيات
"""

import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
from datetime import datetime, timedelta

# إضافة المسار للـ modules
sys.path.append('/home/ubuntu/projects/saudi-stock-ai/backend')

from data.database import Database

def calculate_technical_indicators(df):
    """حساب المؤشرات الفنية"""
    
    # RSI (14 يوم)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_diff'] = df['macd'] - df['macd_signal']
    
    # Moving Averages
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    
    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
    
    # ATR (Average True Range)
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['atr'] = true_range.rolling(14).mean()
    
    # Volume Ratio
    df['volume_ratio'] = df['volume'] / df['volume'].rolling(window=20).mean()
    
    # Price Change
    df['price_change'] = df['close'].pct_change()
    df['price_change_5d'] = df['close'].pct_change(periods=5)
    
    return df

def create_target(df):
    """إنشاء الهدف (Buy/Sell/Hold) بناءً على الحركة المستقبلية"""
    # نظرة للأمام 5 أيام
    df['future_return'] = df['close'].shift(-5) / df['close'] - 1
    
    # تصنيف
    conditions = [
        df['future_return'] > 0.03,  # ارتفاع أكثر من 3% = Buy
        df['future_return'] < -0.03,  # انخفاض أكثر من 3% = Sell
    ]
    choices = ['buy', 'sell']
    df['target'] = np.select(conditions, choices, default='hold')
    
    return df

def prepare_training_data(db):
    """تحضير بيانات التدريب"""
    print("📊 جلب البيانات التاريخية من قاعدة البيانات...")
    
    # جلب آخر 500 يوم من البيانات لكل سهم
    query = """
    SELECT symbol, date, open, high, low, close, volume
    FROM historicalDailyPrices
    WHERE date >= DATE_SUB(CURDATE(), INTERVAL 500 DAY)
    ORDER BY symbol, date
    """
    
    df = pd.read_sql(query, db.connection)
    
    if df.empty:
        print("❌ لا توجد بيانات تاريخية!")
        return None
    
    print(f"✅ تم جلب {len(df)} سجل من {df['symbol'].nunique()} سهم")
    
    # معالجة كل سهم على حدة
    all_data = []
    
    for symbol in df['symbol'].unique():
        stock_df = df[df['symbol'] == symbol].copy()
        stock_df = stock_df.sort_values('date')
        
        # حساب المؤشرات
        stock_df = calculate_technical_indicators(stock_df)
        
        # إنشاء الهدف
        stock_df = create_target(stock_df)
        
        all_data.append(stock_df)
    
    # دمج البيانات
    final_df = pd.concat(all_data, ignore_index=True)
    
    # إزالة الصفوف التي تحتوي على NaN
    final_df = final_df.dropna()
    
    print(f"✅ البيانات النهائية: {len(final_df)} عينة")
    
    return final_df

def train_model(df):
    """تدريب نموذج Random Forest"""
    print("\n🤖 بدء تدريب النموذج...")
    
    # اختيار الميزات
    features = [
        'rsi', 'macd', 'macd_signal', 'macd_diff',
        'sma_20', 'sma_50', 'ema_12',
        'bb_width', 'atr', 'volume_ratio',
        'price_change', 'price_change_5d'
    ]
    
    X = df[features]
    y = df['target']
    
    # تقسيم البيانات
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"📊 بيانات التدريب: {len(X_train)} عينة")
    print(f"📊 بيانات الاختبار: {len(X_test)} عينة")
    print(f"📊 توزيع الفئات:")
    print(y_train.value_counts())
    
    # تدريب النموذج
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=20,
        min_samples_leaf=10,
        class_weight='balanced',  # معالجة عدم التوازن
        random_state=42,
        n_jobs=-1
    )
    
    print("\n⏳ جاري التدريب...")
    model.fit(X_train, y_train)
    
    # التقييم
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✅ دقة النموذج: {accuracy*100:.2f}%")
    print("\n📊 تقرير التصنيف:")
    print(classification_report(y_test, y_pred))
    
    # أهمية الميزات
    feature_importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n📊 أهمية الميزات:")
    print(feature_importance.to_string(index=False))
    
    return model, features

def main():
    print("=" * 60)
    print("🚀 تدريب نموذج Random Forest للتوصيات")
    print("=" * 60)
    
    # الاتصال بقاعدة البيانات
    db = Database()
    
    try:
        # تحضير البيانات
        df = prepare_training_data(db)
        
        if df is None or len(df) < 1000:
            print("❌ البيانات غير كافية للتدريب!")
            print("💡 تحتاج على الأقل 1000 عينة")
            return
        
        # تدريب النموذج
        model, features = train_model(df)
        
        # حفظ النموذج
        model_path = '/tmp/stock_model.pkl'
        model_data = {
            'model': model,
            'features': features,
            'trained_at': datetime.now().isoformat(),
            'samples': len(df)
        }
        
        joblib.dump(model_data, model_path)
        print(f"\n✅ تم حفظ النموذج في: {model_path}")
        
        print("\n" + "=" * 60)
        print("✅ اكتمل التدريب بنجاح!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
