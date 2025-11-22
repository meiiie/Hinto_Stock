import uuid
from datetime import datetime
from typing import Optional, Dict, List
from src.domain.entities.paper_position import PaperPosition
from src.domain.entities.trading_signal import TradingSignal, SignalType
from src.domain.repositories.i_order_repository import IOrderRepository
import logging

logger = logging.getLogger(__name__)

class PaperTradingService:
    """
    Paper Trading Engine (USDT-M Futures).
    Simulates Futures trading with Leverage (Default 1x).
    """
    
    def __init__(self, repository: IOrderRepository):
        self.repo = repository
        self.MAX_POSITIONS = 3
        self.RISK_PER_TRADE = 0.015  # 1.5% risk per trade (Tuned)
        self.LEVERAGE = 1

    def get_wallet_balance(self) -> float:
        """Get Wallet Balance (Total Deposited + Realized PnL)"""
        return self.repo.get_account_balance()

    def get_positions(self) -> List[PaperPosition]:
        """Get all OPEN positions"""
        return self.repo.get_active_orders()

    def calculate_unrealized_pnl(self, current_price: float) -> float:
        """Calculate Total Unrealized PnL of all open positions"""
        positions = self.get_positions()
        total_pnl = 0.0
        for pos in positions:
            total_pnl += pos.calculate_unrealized_pnl(current_price)
        return total_pnl

    def get_margin_balance(self, current_price: float) -> float:
        """Margin Balance = Wallet Balance + Unrealized PnL"""
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
        Handle new trading signal (Limit Order Execution).
        """
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
                # If signal is opposite to current position, Close it (Flip)
                if (pos.side == 'LONG' and signal.signal_type == SignalType.SELL) or \
                   (pos.side == 'SHORT' and signal.signal_type == SignalType.BUY):
                    logger.info(f"🔄 REVERSAL SIGNAL: Closing {pos.side} position. NO FLIP.")
                    self.close_position(pos, signal.price, "SIGNAL_REVERSAL")
                    return # STOP HERE. Do not open new position.
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
        """Close a position and update Wallet Balance"""
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
        
        logger.info(f"💰 CLOSED {position.side} | PnL: ${pnl:.2f} | Reason: {reason}")

    def close_position_by_id(self, position_id: str, current_price: float, reason: str = "MANUAL_CLOSE") -> bool:
        """Close a position by its ID"""
        position = self.repo.get_order(position_id)
        if position and position.status == 'OPEN':
            self.close_position(position, current_price, reason)
            return True
        return False

    def reset_account(self) -> None:
        """Reset paper trading account and data"""
        self.repo.reset_database()
        logger.info("🔄 PAPER TRADING RESET: Database cleared and balance reset to $10,000")

    def process_market_data(self, current_price: float, high: float, low: float) -> None:
        """
        1. Check PENDING orders -> Fill if price hit (Merge if needed) OR TTL Expire.
        2. Check OPEN positions -> SL/TP/Liq.
        """
        # A. Handle PENDING Orders
        pending_orders = self.repo.get_pending_orders()
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

        # B. Handle OPEN Positions
        active_positions = self.get_positions()

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
