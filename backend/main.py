"""
FastAPI Backend لمستشار الأسهم السعودية
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import sys

import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from backend.data.database import Database
from backend.models.ml_model import StockMLModel

# إنشاء التطبيق
app = FastAPI(
    title="Saudi Stock Advisor API",
    description="API لتوصيات الأسهم السعودية باستخدام ML",
    version="1.0.0"
)

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# المتغيرات العامة
db = None
ml_model = None

@app.on_event("startup")
async def startup_event():
    """تشغيل عند بدء التطبيق"""
    global db, ml_model
    
    try:
        # الاتصال بقاعدة البيانات
        db = Database()
        print("✅ تم الاتصال بقاعدة البيانات")
        
        # تحميل نموذج ML
        try:
            ml_model = StockMLModel()
            ml_model.load_model()
            print("✅ تم تحميل نموذج ML")
        except Exception as e:
            print(f"⚠️  لم يتم تحميل نموذج ML: {e}")
            ml_model = None
            
    except Exception as e:
        print(f"❌ خطأ في بدء التطبيق: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """تشغيل عند إيقاف التطبيق"""
    global db
    if db:
        db.close()
        print("✅ تم إغلاق الاتصال بقاعدة البيانات")

# ==================== Endpoints ====================

@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "message": "Saudi Stock Advisor API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """فحص صحة النظام"""
    return {
        "status": "healthy",
        "database": "connected" if db else "disconnected",
        "model": "loaded" if ml_model and ml_model.model else "not loaded",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/stocks")
async def get_stocks(
    limit: int = Query(100, ge=1, le=500),
    sector: Optional[str] = None
):
    """جلب قائمة الأسهم"""
    try:
        if sector:
            query = "SELECT * FROM stocks WHERE isActive = 1 AND sector = %s ORDER BY symbol LIMIT %s"
            stocks = db.fetch_all(query, (sector, limit))
        else:
            query = "SELECT * FROM stocks WHERE isActive = 1 ORDER BY symbol LIMIT %s"
            stocks = db.fetch_all(query, (limit,))
        
        return {
            "count": len(stocks),
            "stocks": stocks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stocks/{symbol}")
async def get_stock(symbol: str):
    """جلب معلومات سهم محدد"""
    try:
        stock = db.get_stock_by_symbol(symbol)
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        # جلب الأسعار التاريخية
        history = db.get_historical_prices(symbol, limit=90)
        
        return {
            "stock": stock,
            "history": history
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recommendations")
async def get_recommendations(limit: int = Query(50, ge=1, le=200)):
    """جلب التوصيات النشطة"""
    try:
        recommendations = db.get_active_recommendations(limit)
        return {
            "count": len(recommendations),
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommendations/generate")
async def generate_recommendations(limit: int = Query(20, ge=1, le=100)):
    """توليد توصيات جديدة باستخدام ML"""
    try:
        if not ml_model or not ml_model.model:
            raise HTTPException(
                status_code=503,
                detail="ML model not loaded. Please train the model first."
            )
        
        # جلب الأسهم
        stocks = db.get_all_stocks()[:limit]
        
        generated_count = 0
        errors = []
        
        for stock in stocks:
            try:
                symbol = stock['symbol']
                
                # جلب البيانات التاريخية
                history = db.get_historical_prices(symbol, limit=100)
                
                if len(history) < 50:
                    continue
                
                # توليد توصية
                recommendation = ml_model.generate_recommendation(symbol, history)
                
                if recommendation:
                    # حفظ التوصية
                    db.insert_recommendation(
                        symbol=symbol,
                        recommendation_type=recommendation['type'],
                        entry_price=recommendation['entry_price'],
                        target_price=recommendation['target_price'],
                        stop_loss=recommendation['stop_loss'],
                        confidence=recommendation['confidence'],
                        analysis=recommendation.get('analysis', '')
                    )
                    generated_count += 1
                    
            except Exception as e:
                errors.append(f"{symbol}: {str(e)}")
                continue
        
        return {
            "generated": generated_count,
            "total_stocks": len(stocks),
            "errors": errors[:10]  # أول 10 أخطاء فقط
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-summary")
async def get_market_summary():
    """جلب ملخص السوق"""
    try:
        query = "SELECT * FROM marketSummary ORDER BY lastUpdate DESC LIMIT 1"
        summary = db.fetch_one(query)
        
        if not summary:
            return {
                "message": "No market summary available",
                "data": None
            }
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sectors")
async def get_sectors():
    """جلب قائمة القطاعات"""
    try:
        query = """
        SELECT sector, COUNT(*) as count, 
               AVG(changePercent) as avg_change
        FROM stocks 
        WHERE isActive = 1 AND sector IS NOT NULL
        GROUP BY sector
        ORDER BY count DESC
        """
        sectors = db.fetch_all(query)
        
        return {
            "count": len(sectors),
            "sectors": sectors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ==================== Trade Evaluation Endpoints ====================

from backend.trade_evaluator import TradeEvaluator

# Initialize Trade Evaluator
trade_evaluator = None

@app.on_event("startup")
async def init_trade_evaluator():
    """تهيئة نظام تقييم الصفقات"""
    global trade_evaluator
    if db:
        trade_evaluator = TradeEvaluator(db)
        print("✅ تم تهيئة نظام تقييم الصفقات")

@app.post("/api/trades/evaluate")
async def evaluate_trades():
    """تقييم جميع الصفقات المفتوحة"""
    try:
        if not trade_evaluator:
            raise HTTPException(status_code=503, detail="Trade evaluator not initialized")
        
        results = trade_evaluator.evaluate_open_trades()
        
        return {
            "status": "success",
            "message": f"تم تقييم {results['total']} صفقة",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trades/history")
async def get_trades_history(limit: int = Query(100, ge=1, le=500)):
    """جلب سجل الصفقات"""
    try:
        if not trade_evaluator:
            raise HTTPException(status_code=503, detail="Trade evaluator not initialized")
        
        trades = trade_evaluator.get_all_trades_history(limit)
        
        return {
            "count": len(trades),
            "trades": trades
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trades/stats")
async def get_daily_stats(date: Optional[str] = None):
    """جلب إحصائيات الأداء اليومية"""
    try:
        if not trade_evaluator:
            raise HTTPException(status_code=503, detail="Trade evaluator not initialized")
        
        from datetime import datetime as dt
        
        if date:
            try:
                date_obj = dt.strptime(date, "%Y-%m-%d").date()
            except:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        else:
            date_obj = None
        
        stats = trade_evaluator.get_daily_stats(date_obj)
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trades/performance")
async def get_overall_performance():
    """جلب الأداء الإجمالي"""
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        query = """
        SELECT 
            COUNT(*) as total_trades,
            SUM(CASE WHEN status = 'target_hit' THEN 1 ELSE 0 END) as successful,
            SUM(CASE WHEN status = 'stop_loss_hit' THEN 1 ELSE 0 END) as failed,
            SUM(CASE WHEN status = 'closed_neutral' THEN 1 ELSE 0 END) as neutral,
            AVG(profit_loss_percent) as avg_return,
            SUM(profit_loss) as total_profit_loss,
            MAX(profit_loss_percent) as best_trade,
            MIN(profit_loss_percent) as worst_trade
        FROM trade_performance
        """
        
        result = db.execute_query(query)
        
        if result and len(result) > 0:
            stats = result[0]
            total = int(stats['total_trades']) if stats['total_trades'] else 0
            successful = int(stats['successful']) if stats['successful'] else 0
            
            return {
                "total_trades": total,
                "successful_trades": successful,
                "failed_trades": int(stats['failed']) if stats['failed'] else 0,
                "neutral_trades": int(stats['neutral']) if stats['neutral'] else 0,
                "success_rate": round((successful / total) * 100, 2) if total > 0 else 0.0,
                "avg_return": float(stats['avg_return']) if stats['avg_return'] else 0.0,
                "total_profit_loss": float(stats['total_profit_loss']) if stats['total_profit_loss'] else 0.0,
                "best_trade": float(stats['best_trade']) if stats['best_trade'] else 0.0,
                "worst_trade": float(stats['worst_trade']) if stats['worst_trade'] else 0.0
            }
        
        return {
            "total_trades": 0,
            "successful_trades": 0,
            "failed_trades": 0,
            "neutral_trades": 0,
            "success_rate": 0.0,
            "avg_return": 0.0,
            "total_profit_loss": 0.0,
            "best_trade": 0.0,
            "worst_trade": 0.0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
