"""
FastAPI Backend لمستشار الأسهم السعودية
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import sys

sys.path.append('/home/ubuntu/projects/saudi-stock-ai')

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
