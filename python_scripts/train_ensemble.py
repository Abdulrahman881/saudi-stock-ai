#!/usr/bin/env python3
"""
تدريب Ensemble Model (Random Forest + XGBoost + LightGBM)
"""

import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from backend.data.database import Database
from backend.models.ml_model import StockMLModel

# تثبيت XGBoost و LightGBM إذا لم يكونا موجودين
try:
    from xgboost import XGBClassifier
    print("✅ XGBoost متاح")
except ImportError:
    print("⚠️  تثبيت XGBoost...")
    os.system("pip install xgboost -q")
    from xgboost import XGBClassifier

try:
    from lightgbm import LGBMClassifier
    print("✅ LightGBM متاح")
except ImportError:
    print("⚠️  تثبيت LightGBM...")
    os.system("pip install lightgbm -q")
    from lightgbm import LGBMClassifier


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
        
        # تحويل Decimal إلى float
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in stock_df.columns:
                stock_df[col] = stock_df[col].astype(float)
        
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


def train_ensemble(df):
    """تدريب Ensemble Model"""
    print("\n🤖 بدء تدريب Ensemble Model...")
    
    # الميزات الكاملة (مع الأنماط الجديدة)
    features = [
        # المؤشرات الأساسية
        'rsi', 'macd', 'macd_signal', 'macd_diff',
        'sma_20', 'sma_50', 'ema_12',
        'bb_width', 'atr', 'volume_ratio',
        'price_change', 'price_change_5d',
        'stoch_k', 'stoch_d', 'adx', 'obv_ema',
        # أنماط الشموع اليابانية
        'doji', 'hammer', 'shooting_star',
        'bullish_engulfing', 'bearish_engulfing',
        'morning_star', 'evening_star',
        # مستويات الدعم والمقاومة
        'dist_from_support', 'dist_from_resistance',
        'sr_position', 'near_support', 'near_resistance'
    ]
    
    # التحقق من وجود الأعمدة
    available_features = [f for f in features if f in df.columns]
    print(f"📊 الميزات المتاحة: {len(available_features)} من {len(features)}")
    
    X = df[available_features]
    y = df['target']
    
    # تقسيم البيانات
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"📊 التدريب: {len(X_train)} عينة")
    print(f"📊 الاختبار: {len(X_test)} عينة")
    print(f"📊 توزيع الفئات:\n{y_train.value_counts()}")
    
    # تحويل الفئات لأرقام لـ XGBoost
    label_map = {'buy': 0, 'hold': 1, 'sell': 2}
    y_train_num = y_train.map(label_map)
    y_test_num = y_test.map(label_map)
    
    # ==================== النماذج ====================
    
    print("\n" + "=" * 50)
    print("🌲 تدريب Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=10,
        min_samples_leaf=5,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_pred)
    print(f"✅ دقة Random Forest: {rf_acc*100:.2f}%")
    
    print("\n" + "=" * 50)
    print("🚀 تدريب XGBoost...")
    xgb_model = XGBClassifier(
        n_estimators=200,
        max_depth=10,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        use_label_encoder=False,
        eval_metric='mlogloss'
    )
    xgb_model.fit(X_train, y_train_num)
    xgb_pred_num = xgb_model.predict(X_test)
    reverse_map = {0: 'buy', 1: 'hold', 2: 'sell'}
    xgb_pred = pd.Series(xgb_pred_num).map(reverse_map)
    xgb_acc = accuracy_score(y_test, xgb_pred)
    print(f"✅ دقة XGBoost: {xgb_acc*100:.2f}%")
    
    print("\n" + "=" * 50)
    print("⚡ تدريب LightGBM...")
    lgb_model = LGBMClassifier(
        n_estimators=200,
        max_depth=10,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    lgb_model.fit(X_train, y_train)
    lgb_pred = lgb_model.predict(X_test)
    lgb_acc = accuracy_score(y_test, lgb_pred)
    print(f"✅ دقة LightGBM: {lgb_acc*100:.2f}%")
    
    # ==================== Ensemble (Voting) ====================
    
    print("\n" + "=" * 50)
    print("🎯 بناء Ensemble Model (Voting)...")
    
    # Soft Voting - يأخذ متوسط الاحتمالات
    ensemble_model = VotingClassifier(
        estimators=[
            ('rf', rf_model),
            ('lgb', lgb_model)
        ],
        voting='soft',
        weights=[1, 1]  # وزن متساوي
    )
    
    ensemble_model.fit(X_train, y_train)
    ensemble_pred = ensemble_model.predict(X_test)
    ensemble_acc = accuracy_score(y_test, ensemble_pred)
    
    print(f"\n✅ دقة Ensemble Model: {ensemble_acc*100:.2f}%")
    
    # ==================== المقارنة ====================
    
    print("\n" + "=" * 50)
    print("📊 مقارنة النماذج:")
    print("=" * 50)
    print(f"  🌲 Random Forest: {rf_acc*100:.2f}%")
    print(f"  🚀 XGBoost:       {xgb_acc*100:.2f}%")
    print(f"  ⚡ LightGBM:      {lgb_acc*100:.2f}%")
    print(f"  🎯 Ensemble:      {ensemble_acc*100:.2f}%")
    
    # اختيار أفضل نموذج
    models = {
        'rf': (rf_model, rf_acc),
        'xgb': (xgb_model, xgb_acc),
        'lgb': (lgb_model, lgb_acc),
        'ensemble': (ensemble_model, ensemble_acc)
    }
    
    best_name = max(models, key=lambda x: models[x][1])
    best_model, best_acc = models[best_name]
    
    print(f"\n🏆 أفضل نموذج: {best_name.upper()} ({best_acc*100:.2f}%)")
    
    # تقرير التصنيف للأفضل
    if best_name == 'xgb':
        best_pred = xgb_pred
    elif best_name == 'rf':
        best_pred = rf_pred
    elif best_name == 'lgb':
        best_pred = lgb_pred
    else:
        best_pred = ensemble_pred
    
    print("\n📊 تقرير التصنيف (أفضل نموذج):")
    print(classification_report(y_test, best_pred))
    
    # أهمية الميزات
    print("\n📊 أهمية الميزات (Random Forest):")
    feature_importance = pd.DataFrame({
        'feature': available_features,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False).head(15)
    print(feature_importance.to_string(index=False))
    
    # استخدام Ensemble كنموذج نهائي
    return ensemble_model, available_features, {
        'rf_acc': rf_acc,
        'xgb_acc': xgb_acc,
        'lgb_acc': lgb_acc,
        'ensemble_acc': ensemble_acc
    }


def main():
    print("=" * 70)
    print("🚀 تدريب Ensemble Model (RF + XGBoost + LightGBM)")
    print("=" * 70)
    
    db = Database()
    
    try:
        # تحضير البيانات
        df = prepare_training_data(db)
        
        if df is None or len(df) < 1000:
            print("❌ البيانات غير كافية!")
            return
        
        # تدريب
        model, features, accuracies = train_ensemble(df)
        
        # حفظ
        ml_model = StockMLModel()
        ml_model.model = model
        ml_model.features = features
        ml_model.save_model()
        
        print("\n" + "=" * 70)
        print("✅ اكتمل التدريب بنجاح!")
        print(f"📊 الدقة النهائية: {accuracies['ensemble_acc']*100:.2f}%")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
