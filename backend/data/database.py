"""
وحدة الاتصال بقاعدة البيانات MySQL
"""

import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional
import os

class Database:
    """فئة للتعامل مع قاعدة البيانات"""
    
    def __init__(self):
        """الاتصال بقاعدة البيانات"""
        self.host = "tradedb.c3o44s2iqqg8.eu-north-1.rds.amazonaws.com"
        self.user = "admin"
        self.password = "0537681225"
        self.database = "saudi_stock_advisor"
        self.connection = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """إنشاء اتصال بقاعدة البيانات"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("✅ تم الاتصال بقاعدة البيانات بنجاح")
        except Error as e:
            print(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
            raise
    
    def close(self):
        """إغلاق الاتصال"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("✅ تم إغلاق الاتصال بقاعدة البيانات")
    
    def execute_query(self, query: str, params: tuple = None):
        """تنفيذ استعلام"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except Error as e:
            print(f"❌ خطأ في تنفيذ الاستعلام: {e}")
            self.connection.rollback()
            return False
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """جلب جميع النتائج"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ خطأ في جلب البيانات: {e}")
            return []
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """جلب نتيجة واحدة"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Error as e:
            print(f"❌ خطأ في جلب البيانات: {e}")
            return None
    
    # دوال خاصة بالأسهم
    
    def get_all_stocks(self) -> List[Dict]:
        """جلب جميع الأسهم"""
        query = "SELECT * FROM stocks WHERE isActive = 1 ORDER BY symbol"
        return self.fetch_all(query)
    
    def get_stock_by_symbol(self, symbol: str) -> Optional[Dict]:
        """جلب سهم محدد"""
        query = "SELECT * FROM stocks WHERE symbol = %s"
        return self.fetch_one(query, (symbol,))
    
    def insert_stock(self, symbol: str, name_ar: str, name_en: str, sector: str = None):
        """إضافة سهم جديد"""
        query = """
        INSERT INTO stocks (symbol, nameAr, nameEn, sector, isActive)
        VALUES (%s, %s, %s, %s, 1)
        ON DUPLICATE KEY UPDATE
        nameAr = VALUES(nameAr),
        nameEn = VALUES(nameEn),
        sector = VALUES(sector)
        """
        return self.execute_query(query, (symbol, name_ar, name_en, sector))
    
    def update_stock_price(self, symbol: str, current_price: float, change: float, change_percent: float):
        """تحديث سعر السهم"""
        query = """
        UPDATE stocks
        SET currentPrice = %s, `change` = %s, changePercent = %s, lastUpdate = NOW()
        WHERE symbol = %s
        """
        return self.execute_query(query, (current_price, change, change_percent, symbol))
    
    # دوال خاصة بالبيانات التاريخية
    
    def insert_historical_price(self, symbol: str, date: str, open_price: float, 
                                high: float, low: float, close: float, volume: int):
        """إضافة سعر تاريخي"""
        query = """
        INSERT INTO historicalDailyPrices (symbol, date, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        open = VALUES(open),
        high = VALUES(high),
        low = VALUES(low),
        close = VALUES(close),
        volume = VALUES(volume)
        """
        return self.execute_query(query, (symbol, date, open_price, high, low, close, volume))
    
    def get_historical_prices(self, symbol: str, limit: int = 100) -> List[Dict]:
        """جلب الأسعار التاريخية لسهم"""
        query = """
        SELECT * FROM historicalDailyPrices
        WHERE symbol = %s
        ORDER BY date DESC
        LIMIT %s
        """
        return self.fetch_all(query, (symbol, limit))
    
    def get_all_historical_data(self, days: int = 500) -> List[Dict]:
        """جلب جميع البيانات التاريخية"""
        query = """
        SELECT * FROM historicalDailyPrices
        WHERE date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        ORDER BY symbol, date
        """
        return self.fetch_all(query, (days,))
    
    # دوال خاصة بالتوصيات
    
    def insert_recommendation(self, symbol: str, recommendation_type: str, 
                             entry_price: float, target_price: float, 
                             stop_loss: float, confidence: float, analysis: str = None):
        """إضافة توصية جديدة"""
        query = """
        INSERT INTO recommendations 
        (symbol, type, entryPrice, targetPrice, stopLoss, confidence, analysis, createdAt)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """
        return self.execute_query(query, (symbol, recommendation_type, entry_price, 
                                         target_price, stop_loss, confidence, analysis))
    
    def get_active_recommendations(self, limit: int = 50) -> List[Dict]:
        """جلب التوصيات النشطة"""
        query = """
        SELECT r.*, s.nameAr, s.nameEn, s.currentPrice, s.sector
        FROM recommendations r
        JOIN stocks s ON r.symbol = s.symbol
        WHERE r.status = 'active'
        AND DATE(r.createdAt) = CURDATE()
        ORDER BY r.confidence DESC, r.createdAt DESC
        LIMIT %s
        """
        return self.fetch_all(query, (limit,))
    
    def save_recommendation(self, symbol: str, recommendation_type: str, 
                           entry_price: float, target_price: float, 
                           stop_loss: float, confidence: float, analysis: str = None):
        """حفظ توصية جديدة (alias لـ insert_recommendation)"""
        return self.insert_recommendation(symbol, recommendation_type, entry_price, 
                                         target_price, stop_loss, confidence, analysis)
    
    def delete_old_recommendations(self, days: int = 7):
        """حذف التوصيات القديمة"""
        query = """
        DELETE FROM recommendations
        WHERE createdAt < DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        return self.execute_query(query, (days,))
