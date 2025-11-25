"""
PerformanceMetrics Entity - Domain Layer

Represents trading performance statistics.
"""

from dataclasses import dataclass
from typing import List
from .paper_position import PaperPosition


@dataclass
class PerformanceMetrics:
    """
    Trading performance metrics calculated from closed trades.
    
    Attributes:
        total_trades: Total number of closed trades
        winning_trades: Number of trades with positive PnL
        losing_trades: Number of trades with negative PnL
        win_rate: Percentage of winning trades (0.0 - 1.0)
        profit_factor: Gross profit / Gross loss
        max_drawdown: Maximum peak-to-trough decline
        total_pnl: Sum of all realized PnL
        average_rr: Average risk/reward ratio achieved
    """
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    max_drawdown: float
    total_pnl: float
    average_rr: float
    
    @classmethod
    def calculate_from_trades(cls, trades: List[PaperPosition]) -> 'PerformanceMetrics':
        """
        Calculate performance metrics from a list of closed trades.
        
        Args:
            trades: List of closed PaperPosition objects
            
        Returns:
            PerformanceMetrics instance
        """
        if not trades:
            return cls(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                profit_factor=0.0,
                max_drawdown=0.0,
                total_pnl=0.0,
                average_rr=0.0
            )
        
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.realized_pnl > 0)
        losing_trades = sum(1 for t in trades if t.realized_pnl < 0)
        
        # Win rate
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        
        # Profit factor
        gross_profit = sum(t.realized_pnl for t in trades if t.realized_pnl > 0)
        gross_loss = abs(sum(t.realized_pnl for t in trades if t.realized_pnl < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf') if gross_profit > 0 else 0.0
        
        # Total PnL
        total_pnl = sum(t.realized_pnl for t in trades)
        
        # Max Drawdown (calculate from equity curve)
        max_drawdown = cls._calculate_max_drawdown(trades)
        
        # Average R:R (simplified - based on actual returns)
        average_rr = cls._calculate_average_rr(trades)
        
        return cls(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            profit_factor=profit_factor,
            max_drawdown=max_drawdown,
            total_pnl=total_pnl,
            average_rr=average_rr
        )
    
    @staticmethod
    def _calculate_max_drawdown(trades: List[PaperPosition]) -> float:
        """Calculate maximum drawdown from trade sequence"""
        if not trades:
            return 0.0
        
        # Sort by close time
        sorted_trades = sorted(
            [t for t in trades if t.close_time],
            key=lambda t: t.close_time
        )
        
        if not sorted_trades:
            return 0.0
        
        # Build equity curve
        equity = 10000.0  # Starting balance
        peak = equity
        max_dd = 0.0
        
        for trade in sorted_trades:
            equity += trade.realized_pnl
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak if peak > 0 else 0.0
            max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    @staticmethod
    def _calculate_average_rr(trades: List[PaperPosition]) -> float:
        """Calculate average risk/reward ratio from trades"""
        if not trades:
            return 0.0
        
        rr_values = []
        for trade in trades:
            if trade.margin > 0:
                # R:R = PnL / Risk (margin)
                rr = trade.realized_pnl / trade.margin
                rr_values.append(rr)
        
        return sum(rr_values) / len(rr_values) if rr_values else 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API response"""
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': round(self.win_rate * 100, 2),  # As percentage
            'profit_factor': round(self.profit_factor, 2),
            'max_drawdown': round(self.max_drawdown * 100, 2),  # As percentage
            'total_pnl': round(self.total_pnl, 2),
            'average_rr': round(self.average_rr, 2)
        }
