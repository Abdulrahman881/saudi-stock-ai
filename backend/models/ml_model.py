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
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> tuple:
        """حساب Stochastic Oscillator"""
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=3).mean()
        return k, d
    
    def calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """حساب ADX (Average Directional Index)"""
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        
        tr = pd.concat([high - low, 
                       np.abs(high - close.shift()), 
                       np.abs(low - close.shift())], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (np.abs(minus_dm).rolling(window=period).mean() / atr)
        
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        return adx
    
    def calculate_obv(self, close: pd.Series, volume: pd.Series) -> pd.Series:
        """حساب OBV (On-Balance Volume)"""
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv
    
    def detect_candlestick_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """اكتشاف أنماط الشموع اليابانية"""
        o = df['open']
        h = df['high']
        l = df['low']
        c = df['close']
        
        # حجم الشمعة
        body = abs(c - o)
        upper_shadow = h - pd.concat([c, o], axis=1).max(axis=1)
        lower_shadow = pd.concat([c, o], axis=1).min(axis=1) - l
        
        # Doji - شمعة التردد
        df['doji'] = (body / (h - l + 0.001) < 0.1).astype(int)
        
        # Hammer - المطرقة (إشارة صعود)
        df['hammer'] = ((lower_shadow > body * 2) & (upper_shadow < body * 0.5) & (c > o)).astype(int)
        
        # Shooting Star - النجمة الساقطة (إشارة هبوط)
        df['shooting_star'] = ((upper_shadow > body * 2) & (lower_shadow < body * 0.5) & (c < o)).astype(int)
        
        # Bullish Engulfing - ابتلاع صعودي
        prev_bearish = (c.shift(1) < o.shift(1))
        curr_bullish = (c > o)
        engulf = (o < c.shift(1)) & (c > o.shift(1))
        df['bullish_engulfing'] = (prev_bearish & curr_bullish & engulf).astype(int)
        
        # Bearish Engulfing - ابتلاع هبوطي
        prev_bullish = (c.shift(1) > o.shift(1))
        curr_bearish = (c < o)
        engulf_bear = (o > c.shift(1)) & (c < o.shift(1))
        df['bearish_engulfing'] = (prev_bullish & curr_bearish & engulf_bear).astype(int)
        
        # Morning Star - نجمة الصباح (إشارة صعود)
        first_bearish = (c.shift(2) < o.shift(2)) & (body.shift(2) > body.shift(2).rolling(10).mean())
        second_small = body.shift(1) < body.shift(2) * 0.5
        third_bullish = (c > o) & (c > (o.shift(2) + c.shift(2)) / 2)
        df['morning_star'] = (first_bearish & second_small & third_bullish).astype(int)
        
        # Evening Star - نجمة المساء (إشارة هبوط)
        first_bullish = (c.shift(2) > o.shift(2)) & (body.shift(2) > body.shift(2).rolling(10).mean())
        third_bearish = (c < o) & (c < (o.shift(2) + c.shift(2)) / 2)
        df['evening_star'] = (first_bullish & second_small & third_bearish).astype(int)
        
        return df
    
    def calculate_support_resistance(self, df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """حساب مستويات الدعم والمقاومة"""
        # مستوى الدعم = أدنى سعر في الفترة
        df['support'] = df['low'].rolling(window=window).min()
        
        # مستوى المقاومة = أعلى سعر في الفترة
        df['resistance'] = df['high'].rolling(window=window).max()
        
        # المسافة من الدعم (%)
        df['dist_from_support'] = ((df['close'] - df['support']) / df['support']) * 100
        
        # المسافة من المقاومة (%)
        df['dist_from_resistance'] = ((df['resistance'] - df['close']) / df['close']) * 100
        
        # نسبة الموقع بين الدعم والمقاومة (0 = عند الدعم, 1 = عند المقاومة)
        df['sr_position'] = (df['close'] - df['support']) / (df['resistance'] - df['support'] + 0.001)
        
        # قرب من الدعم (إشارة شراء)
        df['near_support'] = (df['dist_from_support'] < 2).astype(int)
        
        # قرب من المقاومة (إشارة بيع)
        df['near_resistance'] = (df['dist_from_resistance'] < 2).astype(int)
        
        return df
    
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
        
        # Stochastic Oscillator
        df['stoch_k'], df['stoch_d'] = self.calculate_stochastic(df['high'], df['low'], df['close'])
        
        # ADX
        df['adx'] = self.calculate_adx(df['high'], df['low'], df['close'])
        
        # OBV
        df['obv'] = self.calculate_obv(df['close'], df['volume'])
        df['obv_ema'] = df['obv'].ewm(span=20, adjust=False).mean()
        
        # أنماط الشموع اليابانية
        df = self.detect_candlestick_patterns(df)
        
        # مستويات الدعم والمقاومة
        df = self.calculate_support_resistance(df)
        
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
            
            # حساب نقاط الدخول والخروج (مُحسّن: 4% هدف, 2% وقف)
            if prediction == 'buy':
                entry_price = current_price * 0.99  # 1% أقل
                target_price = current_price * 1.04  # 4% ربح
                stop_loss = current_price * 0.98     # 2% وقف خسارة
            elif prediction == 'sell':
                entry_price = current_price * 1.01  # 1% أعلى
                target_price = current_price * 0.96  # 4% ربح
                stop_loss = current_price * 1.02     # 2% وقف خسارة
            else:  # hold
                entry_price = current_price
                target_price = current_price
                stop_loss = current_price * 0.98
            
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
