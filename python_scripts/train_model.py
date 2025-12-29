#!/usr/bin/env python3
"""
تدريب نموذج Random Forest للتوصيات
"""

import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from datetime import datetime

import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from backend.data.database import Database
from backend.models.ml_model import StockMLModel

def create_target(df):
    """إنشاء الهدف (Buy/Sell/Hold)"""
    # نظرة للأمام 5 أيام
    df['future_return'] = df['close'].shift(-5) / df['close'] - 1
    
    # تصنيف
    conditions = [
        df['future_return'] > 0.03,  # ارتفاع > 3% = Buy
        df['future_return'] < -0.03,  # انخفاض > 3% = Sell
    ]
    choices = ['buy', 'sell']
    df['target'] = np.select(conditions, choices, default='hold')
    
    return df

def prepare_training_data(db):
    """تحضير بيانات التدريب"""
    print("📊 جلب البيانات التاريخية...")
    
    # جلب آخر 500 يوم
    data = db.get_all_historical_data(days=500)
    
    if not data:
        print("❌ لا توجد بيانات!")
        return None
    
    df = pd.DataFrame(data)
    print(f"✅ تم جلب {len(df)} سجل من {df['symbol'].nunique()} سهم")
    
    # معالجة كل سهم
    ml_model = StockMLModel()
    all_data = []
    
    for symbol in df['symbol'].unique():
        stock_df = df[df['symbol'] == symbol].copy()
        stock_df = stock_df.sort_values('date')
        
        # حساب المؤشرات
        stock_df = ml_model.calculate_technical_indicators(stock_df)
        
        # إنشاء الهدف
        stock_df = create_target(stock_df)
        
        all_data.append(stock_df)
    
    # دمج البيانات
    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df.dropna()
    
    print(f"✅ البيانات النهائية: {len(final_df)} عينة")
    
    return final_df

def train_model(df):
    """تدريب النموذج"""
    print("\n🤖 بدء التدريب...")
    
    # الميزات (مع المؤشرات الجديدة)
    features = [
        'rsi', 'macd', 'macd_signal', 'macd_diff',
        'sma_20', 'sma_50', 'ema_12',
        'bb_width', 'atr', 'volume_ratio',
        'price_change', 'price_change_5d',
        'stoch_k', 'stoch_d', 'adx', 'obv_ema'
    ]
    
    X = df[features]
    y = df['target']
    
    # تقسيم البيانات
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"📊 التدريب: {len(X_train)} عينة")
    print(f"📊 الاختبار: {len(X_test)} عينة")
    print(f"📊 توزيع الفئات:\n{y_train.value_counts()}")
    
    # Hyperparameter Tuning
    print("\n⏳ جاري Hyperparameter Tuning...")
    
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [10, 15, 20],
        'min_samples_split': [10, 20],
        'min_samples_leaf': [5, 10]
    }
    
    base_model = RandomForestClassifier(
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    grid_search = GridSearchCV(
        base_model,
        param_grid,
        cv=3,
        scoring='accuracy',
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(X_train, y_train)
    
    print(f"\n✅ أفضل معاملات: {grid_search.best_params_}")
    
    model = grid_search.best_estimator_
    
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
    print("=" * 70)
    print("🚀 تدريب نموذج Random Forest للتوصيات")
    print("=" * 70)
    
    db = Database()
    
    try:
        # تحضير البيانات
        df = prepare_training_data(db)
        
        if df is None or len(df) < 1000:
            print("❌ البيانات غير كافية!")
            return
        
        # تدريب
        model, features = train_model(df)
        
        # حفظ
        ml_model = StockMLModel()
        ml_model.model = model
        ml_model.features = features
        ml_model.save_model()
        
        print("\n" + "=" * 70)
        print("✅ اكتمل التدريب بنجاح!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
