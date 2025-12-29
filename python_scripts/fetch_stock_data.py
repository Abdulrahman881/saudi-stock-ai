#!/usr/bin/env python3
"""
سكريبت لسحب بيانات الأسهم السعودية من Yahoo Finance
"""

import sys
import yfinance as yf
from datetime import datetime, timedelta
import time

# إضافة المسار
sys.path.append('/home/ubuntu/projects/saudi-stock-ai')

from backend.data.database import Database
from python_scripts.saudi_stocks_list import SAUDI_STOCKS

def fetch_stock_data(symbol, db):
    """جلب بيانات سهم واحد"""
    try:
        # إضافة .SR للرمز
        ticker = f"{symbol}.SR"
        
        # جلب البيانات من Yahoo Finance
        stock = yf.Ticker(ticker)
        
        # جلب البيانات التاريخية (آخر 500 يوم)
        hist = stock.history(period="2y")
        
        if hist.empty:
            print(f"  ⚠️  {symbol}: لا توجد بيانات")
            return False
        
        # الحصول على آخر سعر
        latest = hist.iloc[-1]
        current_price = float(latest['Close'])
        
        # حساب التغير
        if len(hist) > 1:
            previous_close = float(hist.iloc[-2]['Close'])
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100
        else:
            change = 0
            change_percent = 0
        
        # تحديث السعر الحالي
        db.update_stock_price(symbol, current_price, change, change_percent)
        
        # إضافة البيانات التاريخية
        count = 0
        for date, row in hist.iterrows():
            date_str = date.strftime('%Y-%m-%d')
            db.insert_historical_price(
                symbol=symbol,
                date=date_str,
                open_price=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=int(row['Volume'])
            )
            count += 1
        
        print(f"  ✅ {symbol}: {current_price:.2f} SAR ({change_percent:+.2f}%) - {count} سجل تاريخي")
        return True
        
    except Exception as e:
        print(f"  ❌ {symbol}: خطأ - {str(e)}")
        return False

def main():
    print("=" * 70)
    print("🚀 سحب بيانات الأسهم السعودية من Yahoo Finance")
    print("=" * 70)
    
    # الاتصال بقاعدة البيانات
    db = Database()
    
    try:
        # إضافة جميع الأسهم إلى قاعدة البيانات
        print(f"\n📊 إضافة {len(SAUDI_STOCKS)} سهم إلى قاعدة البيانات...")
        for stock in SAUDI_STOCKS:
            db.insert_stock(
                symbol=stock["symbol"],
                name_ar=stock["name_ar"],
                name_en=stock["name_en"],
                sector=stock.get("sector", "غير محدد")
            )
        print("✅ تم إضافة جميع الأسهم")
        
        # جلب البيانات
        print(f"\n📈 جلب بيانات الأسهم...")
        success_count = 0
        fail_count = 0
        
        for i, stock in enumerate(SAUDI_STOCKS, 1):
            symbol = stock["symbol"]
            print(f"\n[{i}/{len(SAUDI_STOCKS)}] {stock['name_ar']} ({symbol})")
            
            if fetch_stock_data(symbol, db):
                success_count += 1
            else:
                fail_count += 1
            
            # تأخير بسيط لتجنب Rate Limiting
            time.sleep(0.5)
        
        print("\n" + "=" * 70)
        print("📊 النتائج النهائية:")
        print(f"  ✅ نجح: {success_count} سهم")
        print(f"  ❌ فشل: {fail_count} سهم")
        print(f"  📈 نسبة النجاح: {(success_count/len(SAUDI_STOCKS)*100):.1f}%")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
