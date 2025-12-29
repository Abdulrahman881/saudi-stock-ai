#!/usr/bin/env python3
"""
Backtesting للنموذج على البيانات التاريخية
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from backend.data.database import Database
from backend.models.ml_model import StockMLModel

class Backtester:
    """فئة Backtesting"""
    
    def __init__(self, db, ml_model):
        self.db = db
        self.ml_model = ml_model
        self.trades = []
        
    def backtest(self, start_date, end_date, initial_capital=100000):
        """تشغيل Backtesting"""
        print(f"\n📊 Backtesting من {start_date} إلى {end_date}")
        print(f"💰 رأس المال الأولي: {initial_capital:,.2f} ريال")
        print("=" * 70)
        
        # جلب الأسهم
        stocks = self.db.get_all_stocks()[:30]
        
        total_trades = 0
        successful_trades = 0
        failed_trades = 0
        total_profit = 0
        
        for stock in stocks:
            symbol = stock['symbol']
            
            try:
                # جلب البيانات التاريخية
                history = self.db.get_historical_prices(symbol, limit=500)
                
                if len(history) < 100:
                    continue
                
                # تحويل لـ DataFrame
                df = pd.DataFrame(history)
                
                # تحويل Decimal إلى float
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    if col in df.columns:
                        df[col] = df[col].astype(float)
                
                df = df.sort_values('date')
                
                # حساب المؤشرات
                df = self.ml_model.calculate_technical_indicators(df)
                df = df.dropna()
                
                if len(df) < 50:
                    continue
                
                # محاكاة التداول
                for i in range(50, len(df) - 5):
                    current_row = df.iloc[i]
                    
                    # استخراج الميزات
                    if not self.ml_model.features:
                        continue
                    
                    X = current_row[self.ml_model.features].values.reshape(1, -1)
                    
                    # التنبؤ
                    prediction = self.ml_model.model.predict(X)[0]
                    confidence = self.ml_model.model.predict_proba(X)[0].max() * 100
                    
                    # تجاهل Hold أو ثقة منخفضة
                    if prediction == 'hold' or confidence < 40:
                        continue
                    
                    # نقاط الدخول والخروج
                    entry_price = current_row['close']
                    
                    if prediction == 'buy':
                        target_price = entry_price * 1.05
                        stop_loss = entry_price * 0.97
                    else:  # sell
                        target_price = entry_price * 0.95
                        stop_loss = entry_price * 1.03
                    
                    # محاكاة الصفقة (5 أيام)
                    future_data = df.iloc[i+1:i+6]
                    
                    if len(future_data) == 0:
                        continue
                    
                    # تحقق من وصول الهدف أو وقف الخسارة
                    hit_target = False
                    hit_stop = False
                    exit_price = future_data.iloc[-1]['close']
                    
                    for _, row in future_data.iterrows():
                        if prediction == 'buy':
                            if row['high'] >= target_price:
                                hit_target = True
                                exit_price = target_price
                                break
                            elif row['low'] <= stop_loss:
                                hit_stop = True
                                exit_price = stop_loss
                                break
                        else:  # sell
                            if row['low'] <= target_price:
                                hit_target = True
                                exit_price = target_price
                                break
                            elif row['high'] >= stop_loss:
                                hit_stop = True
                                exit_price = stop_loss
                                break
                    
                    # حساب الربح/الخسارة
                    if prediction == 'buy':
                        profit_loss = exit_price - entry_price
                    else:  # sell
                        profit_loss = entry_price - exit_price
                    
                    profit_loss_percent = (profit_loss / entry_price) * 100
                    
                    # حفظ الصفقة
                    trade = {
                        'symbol': symbol,
                        'type': prediction,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'target_price': target_price,
                        'stop_loss': stop_loss,
                        'profit_loss': profit_loss,
                        'profit_loss_percent': profit_loss_percent,
                        'confidence': confidence,
                        'hit_target': hit_target,
                        'hit_stop': hit_stop,
                        'entry_date': current_row['date'],
                        'exit_date': future_data.iloc[-1]['date']
                    }
                    
                    self.trades.append(trade)
                    total_trades += 1
                    total_profit += profit_loss
                    
                    if hit_target:
                        successful_trades += 1
                    elif hit_stop:
                        failed_trades += 1
                
            except Exception as e:
                print(f"⚠️  خطأ في {symbol}: {e}")
                continue
        
        # النتائج
        print(f"\n📊 نتائج Backtesting:")
        print(f"  ✅ إجمالي الصفقات: {total_trades}")
        print(f"  🎯 وصلت للهدف: {successful_trades}")
        print(f"  ❌ وصلت لوقف الخسارة: {failed_trades}")
        print(f"  ⚠️  أغلقت محايدة: {total_trades - successful_trades - failed_trades}")
        
        if total_trades > 0:
            success_rate = (successful_trades / total_trades) * 100
            print(f"  📈 نسبة النجاح: {success_rate:.2f}%")
            print(f"  💰 إجمالي الربح/الخسارة: {total_profit:,.2f} ريال")
            print(f"  📊 متوسط الربح لكل صفقة: {total_profit/total_trades:,.2f} ريال")
            
            # حساب Sharpe Ratio
            returns = [t['profit_loss_percent'] for t in self.trades]
            sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) > 0 else 0
            print(f"  📈 Sharpe Ratio: {sharpe_ratio:.2f}")
            
            # حساب Max Drawdown
            cumulative_returns = np.cumsum(returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = cumulative_returns - running_max
            max_drawdown = np.min(drawdown)
            print(f"  📉 Max Drawdown: {max_drawdown:.2f}%")
        
        return self.trades

def main():
    print("=" * 70)
    print("🔬 Backtesting نموذج ML")
    print("=" * 70)
    
    db = Database()
    
    try:
        # تحميل النموذج
        ml_model = StockMLModel()
        ml_model.load_model()
        
        if not ml_model.model:
            print("❌ النموذج غير موجود! قم بتدريبه أولاً.")
            return
        
        # تحديد الفترة (آخر سنة)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        
        # تشغيل Backtesting
        backtester = Backtester(db, ml_model)
        trades = backtester.backtest(start_date, end_date)
        
        # حفظ النتائج
        if trades:
            df = pd.DataFrame(trades)
            output_file = f"/tmp/backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(output_file, index=False)
            print(f"\n✅ تم حفظ النتائج في: {output_file}")
        
        print("\n" + "=" * 70)
        print("✅ اكتمل Backtesting بنجاح!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
