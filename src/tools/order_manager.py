import json
import uuid
from phi.tools import Toolkit
from phi.utils.log import logger
from src.db.orders import SQLiteOrdersDB

class OrdersToolkit(Toolkit):
    def __init__(self, db_path: str = "orders.db"):
        super().__init__(name="sqlite_orders_toolkit")
        self.db = SQLiteOrdersDB(db_path=db_path)
        self.register(self.handle_create_order)
        self.register(self.handle_get_status)
        self.register(self.handle_update_status)
        self.register(self.handle_summarize_order_details)

    def generate_customer_id(self) -> str:
        return f"CUST{uuid.uuid4().hex[:8].upper()}"

    def handle_summarize_order_details(self, args: dict) -> str:
        """Initial summary for order - only requires basic product details"""
        required = ["product_name", "size", "price"]
        missing = [field for field in required if field not in args]
        if missing:
            return f"Missing fields for summary: {', '.join(missing)}"
        
        return (
            f"Great choice! The {args['size']} {args['product_name']} is "
            f"{args['price']} with free delivery. Would you like "
            f"to proceed? I'll need your shipping address to continue."
        )

    def handle_create_order(self, args: dict) -> str:
        """Create final order with shipping details"""
        logger.info(f"Creating order with args: {args}")
        required = ["product_name", "size", "price", "shipping_address"]
        missing = [field for field in required if field not in args]
        if missing:
            return f"Missing fields: {', '.join(missing)}"

        price = float(args["price"])
        # Add customer ID and default payment method
        customer_id = self.generate_customer_id()
        args["payment_method"] = args.get("payment_method", "cash")

        # Create the order
        order_id = self.db.create_order(
            customer_id=customer_id,
            product_name=args["product_name"],
            size=args["size"],
            price=price,
            shipping_address=args["shipping_address"],
            payment_method=args["payment_method"]
        )

        if not order_id:
            return "Failed to create order"

        # Get status for delivery date
        status = self.db.get_order_status(order_id)
        
        return (
            f"Perfect! I've created your order. Your order number is {order_id}. "
            f"You can expect delivery by {status['estimated_delivery']}. "
            f"We'll send you a confirmation email with tracking details shortly."
        )

    def handle_get_status(self, args: dict) -> str:
        order_id = args.get("order_id")
        if not order_id:
            return "Order ID is required"
        
        status = self.db.get_order_status(order_id)
        if not status:
            return f"No order found with ID: {order_id}"
        
        return (
            f"Your order {order_id} is currently {status['status']}.\n"
            f"Product: {status['product_name']} ({status['size']})\n"
            f"Expected delivery: {status['estimated_delivery']}"
        )

    def handle_update_status(self, args: dict) -> str:
        order_id = args.get("order_id")
        new_status = args.get("new_status")
        if not order_id or not new_status:
            return "Order ID and new status are required"
        
        if self.db.update_order_status(order_id, new_status):
            return f"Order {order_id} updated to {new_status}"
        return f"Failed to update order {order_id}"