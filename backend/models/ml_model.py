"""
نموذج التعلم الآلي للتوصيات
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
from typing import Dict, List, Optional

class StockMLModel:
    """فئة نموذج ML للتوصيات"""
    
    def __init__(self, model_path: str = "/tmp/stock_model.pkl"):
        """تهيئة النموذج"""
        self.model_path = model_path
        self.model = None
        self.features = None
        
    def load_model(self):
        """تحميل النموذج المدرب"""
        if os.path.exists(self.model_path):
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.features = model_data['features']
            print(f"✅ تم تحميل النموذج من {self.model_path}")
        else:
            print(f"⚠️  النموذج غير موجود في {self.model_path}")
            
    def save_model(self):
        """حفظ النموذج"""
        if self.model and self.features:
            model_data = {
                'model': self.model,
                'features': self.features
            }
            joblib.dump(model_data, self.model_path)
            print(f"✅ تم حفظ النموذج في {self.model_path}")
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """حساب RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series) -> tuple:
        """حساب MACD"""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        diff = macd - signal
        return macd, signal, diff
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> tuple:
        """حساب Bollinger Bands"""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * 2)
        lower = middle - (std * 2)
        width = (upper - lower) / middle
        return middle, upper, lower, width
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """حساب ATR"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = pd.Series(true_range).rolling(period).mean()
        return atr
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """حساب جميع المؤشرات الفنية"""
        # RSI
        df['rsi'] = self.calculate_rsi(df['close'])
        
        # MACD
        df['macd'], df['macd_signal'], df['macd_diff'] = self.calculate_macd(df['close'])
        
        # Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        
        # Bollinger Bands
        df['bb_middle'], df['bb_upper'], df['bb_lower'], df['bb_width'] = \
            self.calculate_bollinger_bands(df['close'])
        
        # ATR
        df['atr'] = self.calculate_atr(df['high'], df['low'], df['close'])
        
        # Volume Ratio
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(window=20).mean()
        
        # Price Changes
        df['price_change'] = df['close'].pct_change()
        df['price_change_5d'] = df['close'].pct_change(periods=5)
        
        return df
    
    def generate_recommendation(self, symbol: str, history: List[Dict]) -> Optional[Dict]:
        """توليد توصية لسهم"""
        try:
            if not self.model or not self.features:
                return None
            
            # تحويل البيانات إلى DataFrame
            df = pd.DataFrame(history)
            df = df.sort_values('date')
            
            # حساب المؤشرات
            df = self.calculate_technical_indicators(df)
            
            # إزالة NaN
            df = df.dropna()
            
            if len(df) < 1:
                return None
            
            # آخر صف
            latest = df.iloc[-1]
            
            # استخراج الميزات
            X = latest[self.features].values.reshape(1, -1)
            
            # التنبؤ
            prediction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            
            # الثقة
            confidence = float(max(probabilities) * 100)
            
            # السعر الحالي
            current_price = float(latest['close'])
            
            # حساب نقاط الدخول والخروج
            if prediction == 'buy':
                entry_price = current_price * 0.98  # 2% أقل
                target_price = current_price * 1.05  # 5% ربح
                stop_loss = current_price * 0.97     # 3% وقف خسارة
            elif prediction == 'sell':
                entry_price = current_price * 1.02  # 2% أعلى
                target_price = current_price * 0.95  # 5% ربح
                stop_loss = current_price * 1.03     # 3% وقف خسارة
            else:  # hold
                entry_price = current_price
                target_price = current_price
                stop_loss = current_price * 0.97
            
            return {
                'type': prediction,
                'entry_price': round(entry_price, 2),
                'target_price': round(target_price, 2),
                'stop_loss': round(stop_loss, 2),
                'confidence': round(confidence, 2),
                'analysis': f"RSI: {latest['rsi']:.1f}, MACD: {latest['macd']:.2f}"
            }
            
        except Exception as e:
            print(f"❌ خطأ في توليد توصية لـ {symbol}: {e}")
            return None
