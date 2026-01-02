import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Callable
from dataclasses import dataclass
from src.domain.entities.paper_position import PaperPosition
from src.domain.entities.trading_signal import TradingSignal, SignalType
from src.domain.entities.portfolio import Portfolio
from src.domain.entities.performance_metrics import PerformanceMetrics
from src.domain.repositories.i_order_repository import IOrderRepository
# SOTA FIX: Import Market Repository for Price Oracle
from src.infrastructure.persistence.sqlite_market_data_repository import SQLiteMarketDataRepository
import logging

logger = logging.getLogger(__name__)


@dataclass
class PaginatedTrades:
    """Paginated trade history result"""
    trades: List[PaperPosition]
    total: int
    page: int
    limit: int
    total_pages: int
    
    def to_dict(self) -> dict:
        return {
            'trades': [
                {
                    'id': t.id,
                    'symbol': t.symbol,
                    'side': t.side,
                    'status': t.status,
                    'entry_price': t.entry_price,
                    'quantity': t.quantity,
                    'margin': t.margin,
                    'stop_loss': t.stop_loss,
                    'take_profit': t.take_profit,
                    'open_time': t.open_time.isoformat() if t.open_time else None,
                    'close_time': t.close_time.isoformat() if t.close_time else None,
                    'realized_pnl': t.realized_pnl,
                    'exit_reason': t.exit_reason
                }
                for t in self.trades
            ],
            'total': self.total,
            'page': self.page,
            'limit': self.limit,
            'total_pages': self.total_pages
        }

class PaperTradingService:
    """
    Paper Trading Engine (USDT-M Futures).
    Simulates Futures trading with Leverage (Default 1x).
    """
    
    # Cooldown durations
    DEFAULT_COOLDOWN_SECONDS = 300  # 5 minutes for normal exits
    REVERSAL_COOLDOWN_SECONDS = 600  # 10 minutes after SIGNAL_REVERSAL
    
    def __init__(self, repository: IOrderRepository, market_data_repository: Optional[SQLiteMarketDataRepository] = None):
        self.repo = repository
        self.market_data_repo = market_data_repository
        self.MAX_POSITIONS = 3
        self.RISK_PER_TRADE = 0.015  # 1.5% risk per trade (Tuned)
        self.LEVERAGE = 1
        
        # CRITICAL FIX: Per-symbol cooldowns (instead of global)
        # This allows trades on ETHUSDT while BTCUSDT is in cooldown
        self._cooldowns: Dict[str, datetime] = {}
        self._cooldown_durations: Dict[str, int] = {}  # Store duration per symbol
        
        # SOTA FIX: Allow position flip (close + open opposite)
        self.ALLOW_FLIP = True
        
        # State Machine Callbacks (ISSUE-001 Fix)
        # Called when a PENDING order is filled and becomes OPEN
        self.on_order_filled: Optional[Callable[[str], None]] = None
        # Called when a position is closed (SL/TP/LIQ/MANUAL)
        self.on_position_closed: Optional[Callable[[str, str], None]] = None

    def get_wallet_balance(self) -> float:
        """Get Wallet Balance (Total Deposited + Realized PnL)"""
        return self.repo.get_account_balance()

    def get_positions(self) -> List[PaperPosition]:
        """Get all OPEN positions"""
        return self.repo.get_active_orders()

    def calculate_unrealized_pnl(self, current_price_override: float = 0.0) -> float:
        """
        Calculate Total Unrealized PnL of all open positions.
        
        SOTA FIX: 
        Uses 'Price Oracle' (MarketDataRepository) to fetch symbol-specific prices.
        Ignores 'current_price_override' unless strictly necessary (single symbol context).
        """
        positions = self.get_positions()
        total_pnl = 0.0
        
        for pos in positions:
            price_to_use = 0.0
            
            # 1. Try to get price from Repository (Priority 1)
            # 1. Try to get price from Repository (Priority 1)
            if self.market_data_repo:
                # 1a. HOT PATH: In-Memory Cache
                price_to_use = self.market_data_repo.get_realtime_price(pos.symbol)
                
                # 1b. COLD PATH: DB Fallback (if cache empty)
                if price_to_use == 0.0:
                    candles = self.market_data_repo.get_latest_candles(pos.symbol, '1m', 1)
                    if candles and len(candles) > 0:
                        price_to_use = candles[0].close
            
            # 2. Fallback to override if logic allows (Weak fallback)
            # Only if we couldn't get price from repo and override is provided
            if price_to_use == 0.0 and current_price_override > 0:
                 price_to_use = current_price_override
                 
            # 3. Calculate PnL for this position
            if price_to_use > 0:
                total_pnl += pos.calculate_unrealized_pnl(price_to_use)
                
        return total_pnl

    def get_positions_with_pnl(self) -> List[dict]:
        """
        Get all open positions enriched with PnL and current price.
        
        SOTA: Returns a View Model (Dictionary) ready for API response.
        Uses correct per-symbol pricing from Repository.
        """
        positions = self.get_positions()
        enriched = []
        
        for pos in positions:
            current_price = 0.0
            
            # Get Price from Repo
            if self.market_data_repo:
                # 1. HOT PATH: In-Memory Cache (Realtime)
                current_price = self.market_data_repo.get_realtime_price(pos.symbol)
                
                # 2. COLD PATH: DB Fallback
                if current_price == 0.0:
                    candles = self.market_data_repo.get_latest_candles(pos.symbol, '1m', 1)
                    if candles and len(candles) > 0:
                        current_price = candles[0].close  # SOTA: MarketData now has .close property
            
            # Fallback (Should not happen in prod if data exists)
            if current_price == 0.0:
                 current_price = pos.entry_price # Prevent division by zero / crazy numbers
            
            pnl = pos.calculate_unrealized_pnl(current_price)
            roe = pos.calculate_roe(current_price)
            
            enriched.append({
                "id": pos.id,
                "symbol": pos.symbol,
                "side": pos.side,
                "status": pos.status,
                "entry_price": pos.entry_price,
                "quantity": pos.quantity,
                "margin": pos.margin,
                "stop_loss": pos.stop_loss,
                "take_profit": pos.take_profit,
                "open_time": pos.open_time.isoformat() if pos.open_time else None,
                "size_usd": pos.quantity * pos.entry_price,
                "current_price": current_price,
                "current_value": pos.quantity * current_price,
                "unrealized_pnl": pnl,
                "roe_pct": roe
            })
            
        return enriched

    def get_margin_balance(self, current_price: float = 0.0) -> float:
        """Margin Balance = Wallet Balance + Unrealized PnL"""
        # SOTA: calculate_unrealized_pnl now handles price lookup internally
        return self.get_wallet_balance() + self.calculate_unrealized_pnl(current_price)

    def get_available_balance(self, current_price: float) -> float:
        """
        Available Balance = Margin Balance - Used Margin (Open + Pending)
        """
        margin_balance = self.get_margin_balance(current_price)
        used_margin = 0.0
        
        # 1. Margin of Open Positions
        for pos in self.get_positions():
            used_margin += pos.margin
            
        # 2. Margin of Pending Orders (Locked)
        pending_orders = self.repo.get_pending_orders()
        for order in pending_orders:
            used_margin += order.margin
            
        return max(0.0, margin_balance - used_margin)

    def on_signal_received(self, signal: TradingSignal, symbol: str = "BTCUSDT") -> None:
        """
        Handle new trading signal.
        
        CRITICAL FIX:
        - Per-symbol cooldown check (was global)
        - Longer cooldown after SIGNAL_REVERSAL (10 min vs 5 min)
        - Allow position flip (close + open opposite direction)
        """
        # CRITICAL FIX: Per-symbol cooldown check
        symbol_key = symbol.lower()
        if symbol_key in self._cooldowns:
            cooldown_duration = self._cooldown_durations.get(
                symbol_key, self.DEFAULT_COOLDOWN_SECONDS
            )
            time_since_close = (datetime.now() - self._cooldowns[symbol_key]).total_seconds()
            if time_since_close < cooldown_duration:
                remaining = int(cooldown_duration - time_since_close)
                logger.info(f"⏸️ COOLDOWN {symbol}: {remaining}s remaining. Signal ignored.")
                return
        
        # 0. Zombie Killer: Cancel existing PENDING orders for this symbol
        pending_orders = self.repo.get_pending_orders()
        for order in pending_orders:
            if order.symbol == symbol:
                logger.info(f"💀 ZOMBIE KILLER: Cancelling old pending order {order.id}")
                order.status = 'CANCELLED'
                order.exit_reason = 'NEW_SIGNAL_OVERRIDE'
                order.close_time = datetime.now()
                self.repo.update_order(order)

        # 1. Check existing positions
        active_positions = self.get_positions()
        for pos in active_positions:
            if pos.symbol == symbol:
                # If signal is opposite to current position
                if (pos.side == 'LONG' and signal.signal_type == SignalType.SELL) or \
                   (pos.side == 'SHORT' and signal.signal_type == SignalType.BUY):
                    logger.info(f"🔄 REVERSAL SIGNAL: Closing {pos.side} position.")
                    self.close_position(pos, signal.price, "SIGNAL_REVERSAL")
                    
                    # CRITICAL FIX: Set per-symbol cooldown with LONGER duration for reversals
                    self._cooldowns[symbol_key] = datetime.now()
                    self._cooldown_durations[symbol_key] = self.REVERSAL_COOLDOWN_SECONDS
                    logger.info(f"⏰ Set {symbol} cooldown: {self.REVERSAL_COOLDOWN_SECONDS}s (REVERSAL)")
                    
                    # SOTA FIX: If ALLOW_FLIP, continue to open new position
                    if not self.ALLOW_FLIP:
                        logger.info("⏹️ FLIP disabled. Not opening opposite position.")
                        return
                    else:
                        logger.info(f"↪️ FLIP enabled. Opening new {signal.signal_type.value.upper()} position.")
                        # Continue to create new position (don't return)
                        break
                else:
                    # Same side -> Allow adding to position (Merging)
                    pass

        if len(active_positions) >= self.MAX_POSITIONS:
            # Only block if we are opening a NEW position (not adding to existing)
            has_position = any(p.symbol == symbol for p in active_positions)
            if not has_position:
                logger.info(f"⚠️ SKIPPED: Max positions reached ({len(active_positions)})")
                return

        # 2. Calculate Position Size
        wallet_balance = self.get_wallet_balance()
        risk_amount = wallet_balance * self.RISK_PER_TRADE
        
        entry_price = signal.entry_price if signal.entry_price else signal.price
        stop_loss = signal.stop_loss if signal.stop_loss else 0.0
        
        if entry_price <= 0: return

        # Calculate Quantity based on Risk
        if stop_loss > 0:
            dist_to_sl = abs(entry_price - stop_loss) / entry_price
            position_size_usd = risk_amount / dist_to_sl if dist_to_sl > 0 else 0
        else:
            position_size_usd = wallet_balance * 0.1 # Default 10% size if no SL

        # Cap size at Available Balance * Leverage
        available_balance = self.get_available_balance(entry_price)
        max_size = available_balance * self.LEVERAGE * 0.95 # 5% buffer
        position_size_usd = min(position_size_usd, max_size)

        if position_size_usd < 10.0:
            logger.info(f"⚠️ SKIPPED: Size too small (${position_size_usd:.2f}) or Insufficient Balance")
            return

        quantity = position_size_usd / entry_price
        margin_required = position_size_usd / self.LEVERAGE

        # 3. Create PENDING Position (Limit Order)
        tp1 = signal.tp_levels.get('tp1', 0.0) if signal.tp_levels else 0.0
        
        # Calculate Liquidation Price (Approximate for Isolated 1x)
        if signal.signal_type == SignalType.BUY:
            liq_price = entry_price - (margin_required / quantity)
        else:
            liq_price = entry_price + (margin_required / quantity)

        position = PaperPosition(
            id=str(uuid.uuid4()),
            symbol=symbol,
            side='LONG' if signal.signal_type == SignalType.BUY else 'SHORT',
            status="PENDING",  # Wait for price
            entry_price=entry_price,
            quantity=quantity,
            leverage=self.LEVERAGE,
            margin=margin_required,
            liquidation_price=liq_price,
            stop_loss=stop_loss,
            take_profit=tp1,
            open_time=datetime.now()
        )
        
        self.repo.save_order(position)
        logger.info(f"⏳ PENDING {position.side} {position.symbol} @ {position.entry_price:.2f} | Size: ${position_size_usd:.2f}")

    def close_position(self, position: PaperPosition, exit_price: float, reason: str) -> None:
        """
        Close a position and update Wallet Balance.
        
        CRITICAL FIX: Sets per-symbol cooldown based on exit reason.
        """
        pnl = position.calculate_unrealized_pnl(exit_price)
        
        position.status = 'CLOSED'
        position.close_time = datetime.now()
        position.realized_pnl = pnl
        position.exit_reason = reason
        
        # Update DB
        self.repo.update_order(position)
        
        # Update Wallet Balance
        current_balance = self.repo.get_account_balance()
        self.repo.update_account_balance(current_balance + pnl)
        
        # CRITICAL FIX: Set per-symbol cooldown based on exit reason
        symbol_key = position.symbol.lower()
        self._cooldowns[symbol_key] = datetime.now()
        
        # Longer cooldown for reversals (indicates ranging market)
        if reason == "SIGNAL_REVERSAL":
            self._cooldown_durations[symbol_key] = self.REVERSAL_COOLDOWN_SECONDS
        else:
            self._cooldown_durations[symbol_key] = self.DEFAULT_COOLDOWN_SECONDS
        
        logger.info(
            f"💰 CLOSED {position.side} | PnL: ${pnl:.2f} | Reason: {reason} | "
            f"Cooldown: {self._cooldown_durations.get(symbol_key, 300)}s"
        )

    def close_position_by_id(self, position_id: str, current_price: float, reason: str = "MANUAL_CLOSE") -> bool:
        """Close a position by its ID"""
        position = self.repo.get_order(position_id)
        if position and position.status == 'OPEN':
            self.close_position(position, current_price, reason)
            
            # ISSUE-001 Fix: Notify state machine of manual close
            if self.on_position_closed:
                try:
                    self.on_position_closed(position_id, reason)
                except Exception as e:
                    logger.error(f"Error in on_position_closed callback: {e}")
            return True
        return False

    def reset_account(self) -> None:
        """Reset paper trading account and data"""
        self.repo.reset_database()
        logger.info("🔄 PAPER TRADING RESET: Database cleared and balance reset to $10,000")

    def process_market_data(self, current_price: float, high: float, low: float, symbol: str) -> None:
        """
        1. Check PENDING orders -> Fill if price hit (Merge if needed) OR TTL Expire.
        2. Check OPEN positions -> SL/TP/Liq.
        
        SOTA FIX: Added 'symbol' parameter to filter processing.
        Prevents applying BTC prices to ETH positions (Cross-Talk Bug).
        """
        # A. Handle PENDING Orders (Filter by Symbol)
        all_pending = self.repo.get_pending_orders()
        pending_orders = [o for o in all_pending if o.symbol.lower() == symbol.lower()]
        
        TTL_SECONDS = 45 * 60 # 45 minutes (3 candles of 15m)

        for order in pending_orders:
            # Check TTL
            time_diff = (datetime.now() - order.open_time).total_seconds()
            if time_diff > TTL_SECONDS:
                logger.info(f"⏰ TTL EXPIRED: Cancelling pending order {order.id}")
                order.status = 'CANCELLED'
                order.exit_reason = 'TTL_EXPIRED'
                order.close_time = datetime.now()
                self.repo.update_order(order)
                continue

            is_filled = False
            if order.side == 'LONG':
                # Buy Limit: Low <= Entry
                if low <= order.entry_price:
                    is_filled = True
            elif order.side == 'SHORT':
                # Sell Limit: High >= Entry
                if high >= order.entry_price:
                    is_filled = True
            
            if is_filled:
                # MERGE LOGIC (One-way Mode)
                existing_positions = [p for p in self.get_positions() if p.symbol == order.symbol and p.side == order.side]
                
                if existing_positions:
                    # Merge into existing position
                    parent_pos = existing_positions[0]
                    
                    total_qty = parent_pos.quantity + order.quantity
                    total_margin = parent_pos.margin + order.margin
                    
                    # Weighted Average Entry Price
                    avg_entry = ((parent_pos.entry_price * parent_pos.quantity) + (order.entry_price * order.quantity)) / total_qty
                    
                    # Update Parent Position
                    parent_pos.entry_price = avg_entry
                    parent_pos.quantity = total_qty
                    parent_pos.margin = total_margin
                    
                    # Recalculate Liquidation Price
                    if parent_pos.side == 'LONG':
                        parent_pos.liquidation_price = avg_entry - (total_margin / total_qty)
                    else:
                        parent_pos.liquidation_price = avg_entry + (total_margin / total_qty)
                        
                    self.repo.update_order(parent_pos)
                    
                    # Mark Pending Order as MERGED (Closed)
                    order.status = 'CLOSED'
                    order.exit_reason = 'MERGED'
                    order.close_time = datetime.now()
                    self.repo.update_order(order)
                    
                    logger.info(f"🔗 MERGED {order.side} {order.symbol} | New Avg Entry: {avg_entry:.2f}")
                    
                else:
                    # No existing position -> Promote to OPEN
                    order.status = 'OPEN'
                    order.open_time = datetime.now() # Update fill time
                    self.repo.update_order(order)
                    logger.info(f"✅ FILLED {order.side} {order.symbol} @ {order.entry_price}")
                    
                    # ISSUE-001 Fix: Notify state machine of order fill
                    if self.on_order_filled:
                        try:
                            self.on_order_filled(order.id)
                        except Exception as e:
                            logger.error(f"Error in on_order_filled callback: {e}")

        # B. Handle OPEN Positions (Filter by Symbol)
        all_positions = self.get_positions()
        active_positions = [p for p in all_positions if p.symbol.lower() == symbol.lower()]

        for pos in active_positions:
            exit_price = None
            reason = None
            
            # --- TRAILING STOP LOGIC (TUNED) ---
            # 1. Update High/Low Watermark
            if pos.side == 'LONG':
                if pos.highest_price == 0 or high > pos.highest_price:
                    pos.highest_price = high
            else:
                if pos.lowest_price == 0 or low < pos.lowest_price:
                    pos.lowest_price = low
            
            # 2. Calculate ROI
            roe = pos.calculate_roe(current_price)
            
            # 3. Step 1: Breakeven Trigger (ROI > 0.8%)
            # Move SL to Entry if not already there
            if roe > 0.8:
                if pos.side == 'LONG':
                    if pos.stop_loss < pos.entry_price:
                        pos.stop_loss = pos.entry_price
                        logger.info(f"🛡️ BREAK EVEN TRIGGERED: {pos.symbol} SL moved to {pos.entry_price}")
                else:
                    if pos.stop_loss == 0 or pos.stop_loss > pos.entry_price:
                        pos.stop_loss = pos.entry_price
                        logger.info(f"🛡️ BREAK EVEN TRIGGERED: {pos.symbol} SL moved to {pos.entry_price}")

            # 4. Step 2: Dynamic Trailing (ROI > 1.2%)
            # Trail by 1.5% distance
            TRAILING_DIST = 0.015 # 1.5%
            
            # Only activate if ROI > 1.2%
            if roe > 1.2:
                if pos.side == 'LONG':
                    # Trail: New SL = High * (1 - Dist)
                    new_sl = pos.highest_price * (1 - TRAILING_DIST)
                    if new_sl > pos.stop_loss:
                        pos.stop_loss = new_sl
                        logger.info(f"🎢 TRAILING STOP: {pos.symbol} SL moved to {new_sl:.2f}")
                else:
                    # Trail: New SL = Low * (1 + Dist)
                    if pos.lowest_price > 0:
                        new_sl = pos.lowest_price * (1 + TRAILING_DIST)
                        if (pos.stop_loss == 0) or (new_sl < pos.stop_loss):
                            pos.stop_loss = new_sl
                            logger.info(f"🎢 TRAILING STOP: {pos.symbol} SL moved to {new_sl:.2f}")

            # Update Position in DB (to save SL changes)
            self.repo.update_order(pos)

            # --- EXIT LOGIC ---
            # 1. Check Liquidation
            if pos.side == 'LONG' and low <= pos.liquidation_price:
                exit_price = pos.liquidation_price
                reason = 'LIQUIDATION'
            elif pos.side == 'SHORT' and high >= pos.liquidation_price:
                exit_price = pos.liquidation_price
                reason = 'LIQUIDATION'
            
            # 2. Check Stop Loss
            elif pos.stop_loss > 0:
                if pos.side == 'LONG' and low <= pos.stop_loss:
                    exit_price = pos.stop_loss
                    reason = 'STOP_LOSS'
                elif pos.side == 'SHORT' and high >= pos.stop_loss:
                    exit_price = pos.stop_loss
                    reason = 'STOP_LOSS'

            # 3. Check Take Profit
            elif pos.take_profit > 0:
                if pos.side == 'LONG' and high >= pos.take_profit:
                    exit_price = pos.take_profit
                    reason = 'TAKE_PROFIT'
                elif pos.side == 'SHORT' and low <= pos.take_profit:
                    exit_price = pos.take_profit
                    reason = 'TAKE_PROFIT'

            if exit_price:
                self.close_position(pos, exit_price, reason)
                
                # ISSUE-001 Fix: Notify state machine of position close
                if self.on_position_closed:
                    try:
                        self.on_position_closed(pos.id, reason)
                    except Exception as e:
                        logger.error(f"Error in on_position_closed callback: {e}")

    # ==================== NEW METHODS FOR DESKTOP APP ====================
    
    def get_portfolio(self, current_price: float = 0.0) -> Portfolio:
        """
        Get current portfolio state.
        
        Args:
            current_price: Current market price for PnL calculation
            
        Returns:
            Portfolio object with balance, equity, positions
        """
        balance = self.get_wallet_balance()
        positions = self.get_positions()
        unrealized_pnl = self.calculate_unrealized_pnl(current_price) if current_price > 0 else 0.0
        
        # Calculate realized PnL from closed trades
        closed_trades = self.repo.get_closed_orders(limit=1000)
        realized_pnl = sum(t.realized_pnl for t in closed_trades)
        
        equity = balance + unrealized_pnl
        
        return Portfolio(
            balance=balance,
            equity=equity,
            unrealized_pnl=unrealized_pnl,
            realized_pnl=realized_pnl,
            open_positions=positions
        )
    
    def get_trade_history(
        self, page: int = 1, limit: int = 20,
        symbol: Optional[str] = None,
        side: Optional[str] = None,
        pnl_filter: Optional[str] = None
    ) -> PaginatedTrades:
        """
        Get paginated trade history with optional filters.
        
        SOTA Phase 24c: Server-side filtering support.
        
        Args:
            page: Page number (1-indexed)
            limit: Items per page
            symbol: Optional filter by symbol
            side: Optional filter by side ('LONG'/'SHORT')
            pnl_filter: Optional 'profit' or 'loss' filter
            
        Returns:
            PaginatedTrades with trades and pagination info
        """
        trades, total = self.repo.get_closed_orders_paginated(
            page, limit, symbol=symbol, side=side, pnl_filter=pnl_filter
        )
        total_pages = (total + limit - 1) // limit  # Ceiling division
        
        return PaginatedTrades(
            trades=trades,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    
    def calculate_performance(self, days: int = 7) -> PerformanceMetrics:
        """
        Calculate performance metrics for the specified period.
        
        Args:
            days: Number of days to analyze (default: 7)
            
        Returns:
            PerformanceMetrics object
        """
        # Get all closed trades (we'll filter by date)
        all_trades = self.repo.get_closed_orders(limit=10000)
        
        # Filter by date range
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_trades = [
            t for t in all_trades 
            if t.close_time and t.close_time >= cutoff_date
        ]
        
        return PerformanceMetrics.calculate_from_trades(recent_trades)
    
    # ==================== SETTINGS METHODS ====================
    
    def get_settings(self) -> dict:
        """Get all trading settings"""
        settings = self.repo.get_all_settings()
        
        # Return with defaults if not set
        return {
            'risk_percent': float(settings.get('risk_percent', '1.5')),
            'rr_ratio': float(settings.get('rr_ratio', '1.5')),
            'max_positions': int(settings.get('max_positions', '3')),
            'leverage': int(settings.get('leverage', '1')),
            'auto_execute': settings.get('auto_execute', 'false') == 'true'
        }
    
    def update_settings(self, settings: dict) -> dict:
        """
        Update trading settings.
        
        Args:
            settings: Dict with setting keys and values
            
        Returns:
            Updated settings dict
        """
        allowed_keys = ['risk_percent', 'rr_ratio', 'max_positions', 'leverage', 'auto_execute']
        
        for key, value in settings.items():
            if key in allowed_keys:
                # Convert bool to string for storage
                if isinstance(value, bool):
                    value = 'true' if value else 'false'
                self.repo.set_setting(key, str(value))
                
                # Apply to service immediately
                if key == 'risk_percent':
                    self.RISK_PER_TRADE = float(value) / 100
                elif key == 'max_positions':
                    self.MAX_POSITIONS = int(value)
                elif key == 'leverage':
                    self.LEVERAGE = int(value)
        
        logger.info(f"📝 Settings updated: {settings}")
        return self.get_settings()
    
    def execute_trade(self, signal: TradingSignal, symbol: str = "BTCUSDT") -> Optional[str]:
        """
        Execute a trade from a signal (wrapper for on_signal_received).
        
        Args:
            signal: Trading signal to execute
            symbol: Trading symbol
            
        Returns:
            Position ID if created, None otherwise
        """
        # Store current position count
        before_count = len(self.get_positions()) + len(self.repo.get_pending_orders())
        
        # Execute via existing method
        self.on_signal_received(signal, symbol)
        
        # Check if new position was created
        after_count = len(self.get_positions()) + len(self.repo.get_pending_orders())
        
        if after_count > before_count:
            # Return the latest pending order ID
            pending = self.repo.get_pending_orders()
            if pending:
                return pending[-1].id
        
        return None
