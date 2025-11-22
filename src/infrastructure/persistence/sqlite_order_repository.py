import sqlite3
from typing import List, Optional
from datetime import datetime
from contextlib import contextmanager
from src.domain.entities.paper_position import PaperPosition
from src.domain.repositories.i_order_repository import IOrderRepository

class SQLiteOrderRepository(IOrderRepository):
    """SQLite implementation of Position Repository (Futures)"""
    
    def __init__(self, db_path: str = "data/trading_system.db"):
        self.db_path = db_path

    @contextmanager
    def _get_connection(self):
        """Context manager for database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def save_order(self, position: PaperPosition) -> None:
        """Save a new position"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO paper_positions (
                    id, symbol, side, status, entry_price, quantity, 
                    leverage, margin, liquidation_price,
                    stop_loss, take_profit, 
                    open_time, close_time, realized_pnl, exit_reason,
                    highest_price, lowest_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                position.id, position.symbol, position.side, position.status, 
                position.entry_price, position.quantity, 
                position.leverage, position.margin, position.liquidation_price,
                position.stop_loss, position.take_profit, 
                position.open_time.isoformat(), 
                position.close_time.isoformat() if position.close_time else None, 
                position.realized_pnl, position.exit_reason,
                position.highest_price, position.lowest_price
            ))
            conn.commit()

    def update_order(self, position: PaperPosition) -> None:
        """Update an existing position"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE paper_positions SET
                    status = ?,
                    close_time = ?,
                    realized_pnl = ?,
                    exit_reason = ?,
                    entry_price = ?,
                    quantity = ?,
                    margin = ?,
                    liquidation_price = ?,
                    stop_loss = ?,
                    highest_price = ?,
                    lowest_price = ?
                WHERE id = ?
            ''', (
                position.status,
                position.close_time.isoformat() if position.close_time else None,
                position.realized_pnl,
                position.exit_reason,
                position.entry_price,
                position.quantity,
                position.margin,
                position.liquidation_price,
                position.stop_loss,
                position.highest_price,
                position.lowest_price,
                position.id
            ))
            conn.commit()

    def get_order(self, position_id: str) -> Optional[PaperPosition]:
        """Get position by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM paper_positions WHERE id = ?', (position_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_position(row)
            return None

    def get_active_orders(self) -> List[PaperPosition]:
        """Get all active positions (OPEN)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM paper_positions WHERE status = 'OPEN'")
            rows = cursor.fetchall()
            return [self._row_to_position(row) for row in rows]

    def get_pending_orders(self) -> List[PaperPosition]:
        """Get all pending orders (PENDING)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM paper_positions WHERE status = 'PENDING'")
            rows = cursor.fetchall()
            return [self._row_to_position(row) for row in rows]

    def get_closed_orders(self, limit: int = 50) -> List[PaperPosition]:
        """Get closed positions"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM paper_positions WHERE status = 'CLOSED' ORDER BY close_time DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [self._row_to_position(row) for row in rows]

    def get_account_balance(self) -> float:
        """Get current wallet balance"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT balance FROM paper_account WHERE id = 1')
            row = cursor.fetchone()
            if row:
                return row['balance']
            return 10000.0 # Default fallback

    def update_account_balance(self, balance: float) -> None:
        """Update wallet balance"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE paper_account SET balance = ? WHERE id = 1', (balance,))
            conn.commit()

    def _row_to_position(self, row) -> PaperPosition:
        """Convert DB row to PaperPosition object"""
        # Handle new columns if they exist (or default to 0.0)
        # Since we are using sqlite3.Row, we can check keys or use try/except
        try:
            highest_price = row['highest_price']
            lowest_price = row['lowest_price']
        except IndexError: # If accessed by index
             highest_price = 0.0
             lowest_price = 0.0
        except ValueError: # If accessed by name but missing
             highest_price = 0.0
             lowest_price = 0.0
        except: # Fallback
             highest_price = 0.0
             lowest_price = 0.0

        return PaperPosition(
            id=row['id'],
            symbol=row['symbol'],
            side=row['side'],
            status=row['status'],
            entry_price=row['entry_price'],
            quantity=row['quantity'],
            leverage=row['leverage'],
            margin=row['margin'],
            liquidation_price=row['liquidation_price'],
            stop_loss=row['stop_loss'],
            take_profit=row['take_profit'],
            open_time=datetime.fromisoformat(row['open_time']),
            close_time=datetime.fromisoformat(row['close_time']) if row['close_time'] else None,
            realized_pnl=row['realized_pnl'],
            exit_reason=row['exit_reason'],
            lowest_price=lowest_price
        )

    def reset_database(self) -> None:
        """Reset database (Clear all data)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Clear tables
            cursor.execute("DELETE FROM paper_positions")
            # Reset account balance
            cursor.execute("UPDATE paper_account SET balance = 10000.0 WHERE id = 1")
            conn.commit()
