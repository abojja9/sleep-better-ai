# orders.py
import sqlite3
from datetime import datetime, timedelta

class SQLiteOrdersDB:
    def __init__(self, db_path: str = "orders.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Create the orders table with essential fields."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT,
                product_name TEXT,
                size TEXT,
                price REAL,
                status TEXT,
                order_date TEXT,
                estimated_delivery TEXT,
                shipping_address TEXT,
                payment_method TEXT,
                confirmed BOOLEAN DEFAULT FALSE
            )
        """)
        conn.commit()
        conn.close()

    def create_order_draft(self, customer_id: str, product_name: str, size: str, price: float, shipping_address: str = None) -> str:
        """Create a draft order pending confirmation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        count = cursor.fetchone()[0]
        order_id = f"ORD{count + 1:06d}"
        
        # Set fixed 7-day delivery estimate
        order_date = datetime.now()
        estimated_delivery = (order_date + timedelta(days=7)).isoformat()
        
        cursor.execute("""
            INSERT INTO orders (
                order_id, customer_id, product_name, size, price, 
                status, order_date, estimated_delivery, shipping_address, 
                confirmed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_id, customer_id, product_name, size, price,
            "draft", order_date.isoformat(), estimated_delivery, 
            shipping_address, False
        ))
        conn.commit()
        conn.close()
        return order_id

    def confirm_order(self, order_id: str, payment_method: str, shipping_address: str) -> bool:
        """Confirm a draft order with payment and shipping details."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE orders 
            SET status = 'processing',
                confirmed = TRUE,
                payment_method = ?,
                shipping_address = ?
            WHERE order_id = ? AND confirmed = FALSE
        """, (payment_method, shipping_address, order_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def create_order(self, customer_id: str, product_name: str, size: str, price: float, shipping_address: str, payment_method: str) -> str:
        """
        Directly create and confirm an order with the provided details.
        
        Returns the order_id if successful, or None if creation fails.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generate a new order_id based on the current count of orders
        cursor.execute("SELECT COUNT(*) FROM orders")
        count = cursor.fetchone()[0]
        order_id = f"ORD{count + 1:06d}"
        
        # Set fixed 7-day delivery estimate
        order_date = datetime.now()
        estimated_delivery = (order_date + timedelta(days=7)).isoformat()
        
        cursor.execute("""
            INSERT INTO orders (
                order_id, customer_id, product_name, size, price, 
                status, order_date, estimated_delivery, shipping_address, 
                payment_method, confirmed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_id, customer_id, product_name, size, price,
            "processing", order_date.isoformat(), estimated_delivery, 
            shipping_address, payment_method, True
        ))
        
        conn.commit()
        conn.close()
        return order_id

    def get_order_status(self, order_id: str):
        """Fetch order status with formatted delivery date."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT status, order_date, estimated_delivery, product_name, size, price 
            FROM orders 
            WHERE order_id = ?
        """, (order_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            status, order_date, estimated_delivery, product_name, size, price = row
            # Format delivery date for display
            delivery_date = datetime.fromisoformat(estimated_delivery).strftime('%B %d, %Y')
            return {
                "order_id": order_id,
                "status": status,
                "order_date": order_date,
                "estimated_delivery": delivery_date,
                "product_name": product_name,
                "size": size,
                "price": price
            }
        return None

    def update_order_status(self, order_id: str, new_status: str) -> bool:
        """Update the status of a given order."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", (new_status, order_id))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0