#!/usr/bin/env python3
"""
سكريبت التقييم اليومي للصفقات
يعمل كل يوم الساعة 5 عصراً
"""

import sys
import os
from datetime import datetime

# إضافة المسار الحالي
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from backend.data.database import Database
from backend.trade_evaluator import TradeEvaluator
from backend.models.ml_model import StockMLModel

def main():
    print("=" * 70)
    print("🔄 بدء التقييم اليومي للصفقات")
    print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    db = None
    
    try:
        # الاتصال بقاعدة البيانات
        print("\n📊 الاتصال بقاعدة البيانات...")
        db = Database()
        db.connect()
        print("✅ تم الاتصال بنجاح")
        
        # تهيئة نظام التقييم
        evaluator = TradeEvaluator(db)
        
        # تقييم الصفقات المفتوحة
        print("\n🔍 تقييم الصفقات المفتوحة...")
        results = evaluator.evaluate_open_trades()
        
        print(f"\n📊 النتائج:")
        print(f"  ✅ إجمالي الصفقات: {results['total']}")
        print(f"  🎯 وصلت للهدف: {results['target_hit']}")
        print(f"  ❌ وصلت لوقف الخسارة: {results['stop_loss_hit']}")
        print(f"  ⚠️  أغلقت محايدة: {results['closed_neutral']}")
        print(f"  📈 نسبة النجاح: {results['success_rate']}%")
        
        # حفظ الإحصائيات اليومية
        stats = evaluator.get_daily_stats()
        print(f"\n📊 إحصائيات اليوم:")
        print(f"  💰 إجمالي الربح/الخسارة: {stats['total_profit_loss']:.2f} SAR")
        print(f"  📈 متوسط الربح: {stats['avg_profit']:.2f} SAR")
        print(f"  📉 متوسط الخسارة: {stats['avg_loss']:.2f} SAR")
        
        # توليد توصيات جديدة
        print("\n🤖 توليد توصيات جديدة...")
        
        try:
            ml_model = StockMLModel()
            ml_model.load_model()
            
            # جلب الأسهم النشطة
            stocks_query = "SELECT symbol FROM stocks WHERE isActive = 1 LIMIT 30"
            stocks = db.execute_query(stocks_query)
            
            recommendations_count = 0
            
            for stock in stocks:
                symbol = stock['symbol']
                
                try:
                    # جلب البيانات التاريخية
                    history = db.get_historical_prices(symbol, limit=100)
                    
                    if len(history) < 50:
                        continue
                    
                    # التنبؤ
                    prediction = ml_model.predict_stock(history)
                    
                    if prediction and prediction['recommendation'] in ['buy', 'sell']:
                        # حفظ التوصية
                        db.save_recommendation(
                            symbol=symbol,
                            recommendation_type=prediction['recommendation'],
                            entry_price=prediction['entry_price'],
                            target_price=prediction['target_price'],
                            stop_loss=prediction['stop_loss'],
                            confidence=prediction['confidence'],
                            analysis=f"ML Prediction - Confidence: {prediction['confidence']:.2f}%"
                        )
                        recommendations_count += 1
                        
                except Exception as e:
                    print(f"  ⚠️  خطأ في {symbol}: {e}")
                    continue
            
            print(f"✅ تم توليد {recommendations_count} توصية جديدة")
            
        except Exception as e:
            print(f"⚠️  لم يتم توليد توصيات جديدة: {e}")
        
        print("\n" + "=" * 70)
        print("✅ اكتمل التقييم اليومي بنجاح")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        if db:
            db.close()
            print("\n✅ تم إغلاق الاتصال بقاعدة البيانات")

if __name__ == "__main__":
    main()
