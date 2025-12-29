"""
نظام تقييم الصفقات اليومية
"""

from datetime import datetime, timedelta
from typing import List, Dict
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from backend.data.database import Database

class TradeEvaluator:
    def __init__(self, db: Database):
        self.db = db
    
    def evaluate_open_trades(self) -> Dict:
        """
        تقييم جميع الصفقات المفتوحة
        """
        # جلب الصفقات المفتوحة (غير المقيّمة)
        query = """
        SELECT 
            r.id,
            r.symbol,
            r.entryPrice,
            r.targetPrice,
            r.stopLoss,
            r.createdAt,
            s.currentPrice,
            s.changePercent
        FROM recommendations r
        JOIN stocks s ON r.symbol = s.symbol
        WHERE r.is_evaluated = 0
        AND r.status = 'active'
        AND DATE(r.createdAt) < CURDATE()
        ORDER BY r.createdAt DESC
        """
        
        open_trades = self.db.fetch_all(query)
        
        results = {
            'total': 0,
            'target_hit': 0,
            'stop_loss_hit': 0,
            'closed_neutral': 0,
            'trades': []
        }
        
        for trade in open_trades:
            evaluation = self._evaluate_single_trade(trade)
            results['trades'].append(evaluation)
            results['total'] += 1
            
            if evaluation['status'] == 'target_hit':
                results['target_hit'] += 1
            elif evaluation['status'] == 'stop_loss_hit':
                results['stop_loss_hit'] += 1
            else:
                results['closed_neutral'] += 1
        
        # حساب الإحصائيات
        if results['total'] > 0:
            results['success_rate'] = round((results['target_hit'] / results['total']) * 100, 2)
        else:
            results['success_rate'] = 0.0
        
        return results
    
    def _evaluate_single_trade(self, trade: Dict) -> Dict:
        """
        تقييم صفقة واحدة
        """
        symbol = trade['symbol']
        entry_price = float(trade['entryPrice'])
        target_price = float(trade['targetPrice'])
        stop_loss = float(trade['stopLoss'])
        current_price = float(trade['currentPrice'])
        entry_date = trade['createdAt']
        
        # جلب أعلى وأقل سعر خلال فترة الصفقة
        high_low_query = """
        SELECT 
            MAX(high) as highest,
            MIN(low) as lowest
        FROM historicalDailyPrices
        WHERE symbol = %s
        AND date >= DATE(%s)
        AND date <= CURDATE()
        """
        
        high_low = self.db.fetch_all(high_low_query, (symbol, entry_date))
        
        if high_low and len(high_low) > 0:
            highest = float(high_low[0]['highest']) if high_low[0]['highest'] else current_price
            lowest = float(high_low[0]['lowest']) if high_low[0]['lowest'] else current_price
        else:
            highest = current_price
            lowest = current_price
        
        # تحديد حالة الصفقة
        status = 'closed_neutral'
        exit_price = current_price
        
        if highest >= target_price:
            status = 'target_hit'
            exit_price = target_price
        elif lowest <= stop_loss:
            status = 'stop_loss_hit'
            exit_price = stop_loss
        
        # حساب الربح/الخسارة
        profit_loss = exit_price - entry_price
        profit_loss_percent = round(((exit_price - entry_price) / entry_price) * 100, 2)
        
        # حفظ النتيجة في قاعدة البيانات
        self._save_trade_performance(
            recommendation_id=trade['id'],
            symbol=symbol,
            entry_price=entry_price,
            target_price=target_price,
            stop_loss=stop_loss,
            exit_price=exit_price,
            entry_date=entry_date,
            exit_date=datetime.now(),
            status=status,
            profit_loss=profit_loss,
            profit_loss_percent=profit_loss_percent,
            highest=highest,
            lowest=lowest
        )
        
        # تحديث حالة التوصية
        update_query = """
        UPDATE recommendations
        SET is_evaluated = 1,
            evaluation_date = NOW(),
            status = 'evaluated'
        WHERE id = %s
        """
        self.db.execute_query(update_query, (trade['id'],))
        
        return {
            'recommendation_id': trade['id'],
            'symbol': symbol,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'status': status,
            'profit_loss': profit_loss,
            'profit_loss_percent': profit_loss_percent,
            'highest': highest,
            'lowest': lowest,
            'entry_date': entry_date,
            'exit_date': datetime.now()
        }
    
    def _save_trade_performance(self, **kwargs):
        """
        حفظ أداء الصفقة في قاعدة البيانات
        """
        query = """
        INSERT INTO trade_performance (
            recommendation_id, symbol, entry_price, target_price, stop_loss,
            exit_price, entry_date, exit_date, status, profit_loss,
            profit_loss_percent, high_during_trade, low_during_trade
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        self.db.execute_query(query, (
            kwargs['recommendation_id'],
            kwargs['symbol'],
            kwargs['entry_price'],
            kwargs['target_price'],
            kwargs['stop_loss'],
            kwargs['exit_price'],
            kwargs['entry_date'],
            kwargs['exit_date'],
            kwargs['status'],
            kwargs['profit_loss'],
            kwargs['profit_loss_percent'],
            kwargs['highest'],
            kwargs['lowest']
        ))
    
    def get_daily_stats(self, date=None) -> Dict:
        """
        جلب إحصائيات يوم محدد
        """
        if date is None:
            date = datetime.now().date()
        
        query = """
        SELECT 
            COUNT(*) as total_trades,
            SUM(CASE WHEN status = 'target_hit' THEN 1 ELSE 0 END) as successful_trades,
            SUM(CASE WHEN status = 'stop_loss_hit' THEN 1 ELSE 0 END) as failed_trades,
            SUM(CASE WHEN status = 'closed_neutral' THEN 1 ELSE 0 END) as neutral_trades,
            AVG(CASE WHEN profit_loss > 0 THEN profit_loss ELSE NULL END) as avg_profit,
            AVG(CASE WHEN profit_loss < 0 THEN profit_loss ELSE NULL END) as avg_loss,
            SUM(profit_loss) as total_profit_loss
        FROM trade_performance
        WHERE DATE(exit_date) = %s
        """
        
        result = self.db.fetch_all(query, (date,))
        
        if result and len(result) > 0:
            stats = result[0]
            total = int(stats['total_trades']) if stats['total_trades'] else 0
            successful = int(stats['successful_trades']) if stats['successful_trades'] else 0
            
            success_rate = round((successful / total) * 100, 2) if total > 0 else 0.0
            
            return {
                'date': str(date),
                'total_trades': total,
                'successful_trades': successful,
                'failed_trades': int(stats['failed_trades']) if stats['failed_trades'] else 0,
                'neutral_trades': int(stats['neutral_trades']) if stats['neutral_trades'] else 0,
                'success_rate': success_rate,
                'avg_profit': float(stats['avg_profit']) if stats['avg_profit'] else 0.0,
                'avg_loss': float(stats['avg_loss']) if stats['avg_loss'] else 0.0,
                'total_profit_loss': float(stats['total_profit_loss']) if stats['total_profit_loss'] else 0.0
            }
        
        return {
            'date': str(date),
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'neutral_trades': 0,
            'success_rate': 0.0,
            'avg_profit': 0.0,
            'avg_loss': 0.0,
            'total_profit_loss': 0.0
        }
    
    def get_all_trades_history(self, limit=100) -> List[Dict]:
        """
        جلب سجل جميع الصفقات
        """
        query = """
        SELECT 
            tp.*,
            r.type as recommendation_type,
            r.confidence
        FROM trade_performance tp
        LEFT JOIN recommendations r ON tp.recommendation_id = r.id
        ORDER BY tp.exit_date DESC
        LIMIT %s
        """
        
        trades = self.db.fetch_all(query, (limit,))
        
        return [
            {
                'id': trade['id'],
                'symbol': trade['symbol'],
                'entry_price': float(trade['entry_price']),
                'exit_price': float(trade['exit_price']),
                'target_price': float(trade['target_price']),
                'stop_loss': float(trade['stop_loss']),
                'status': trade['status'],
                'profit_loss': float(trade['profit_loss']),
                'profit_loss_percent': float(trade['profit_loss_percent']),
                'entry_date': trade['entry_date'],
                'exit_date': trade['exit_date'],
                'recommendation_type': trade.get('recommendation_type'),
                'confidence': float(trade['confidence']) if trade.get('confidence') else None
            }
            for trade in trades
        ]
