# tests/test_orders_db.py
import pytest
from datetime import datetime, timedelta
import sqlite3
from src.db.orders import SQLiteOrdersDB

# Setup fixture
@pytest.fixture(autouse=True)
def setup_teardown():
    """Setup and teardown for each test"""
    # Setup
    yield
    # Teardown - database is automatically cleaned up since we're using :memory:

@pytest.fixture
def orders_db():
    """Create a temporary in-memory database for testing"""
    db = SQLiteOrdersDB(db_path="data/db/orders.sqlite")
    print("Database initialized")
    return db

def test_create_order_draft(orders_db):
    """Test creating a draft order"""
    order_id = orders_db.create_order_draft(
        customer_id="CUST123",
        product_name="Ultra Comfort Mattress",
        size="Queen",
        price=1299.00,
        shipping_address="123 Test St"
    )
    
    # Verify order creation
    assert order_id is not None
    assert order_id.startswith("ORD")
    
    # Verify order status
    order_status = orders_db.get_order_status(order_id)
    assert order_status["status"] == "draft"
    assert order_status["product_name"] == "Ultra Comfort Mattress"
    assert order_status["size"] == "Queen"
    assert order_status["price"] == 1299.00

def test_confirm_order(orders_db):
    """Test order confirmation process"""
    # Create draft order
    order_id = orders_db.create_order_draft(
        customer_id="CUST123",
        product_name="Ultra Comfort Mattress",
        size="Queen",
        price=1299.00,
        shipping_address="123 Test St"
    )
    
    # Confirm order
    result = orders_db.confirm_order(
        order_id=order_id,
        payment_method="credit_card",
        shipping_address="123 Test St"
    )
    assert result is True

    # Verify order status changed to processing
    order_status = orders_db.get_order_status(order_id)
    assert order_status["status"] == "processing"
    assert order_status["product_name"] == "Ultra Comfort Mattress"

def test_order_status_updates(orders_db):
    """Test updating order status"""
    # Create and confirm order
    order_id = orders_db.create_order_draft(
        customer_id="CUST123",
        product_name="Dream Sleep Mattress",
        size="King",
        price=899.00,
        shipping_address="456 Test Ave"
    )
    orders_db.confirm_order(order_id, "credit_card", "456 Test Ave")
    
    # Update status
    updated = orders_db.update_order_status(order_id, "shipped")
    assert updated is True
    
    # Verify new status
    order_status = orders_db.get_order_status(order_id)
    assert order_status["status"] == "shipped"

def test_nonexistent_order(orders_db):
    """Test handling of non-existent orders"""
    # Get status of non-existent order
    status = orders_db.get_order_status("NONEXISTENT")
    assert status is None
    
    # Try to update non-existent order
    updated = orders_db.update_order_status("NONEXISTENT", "processing")
    assert updated is False