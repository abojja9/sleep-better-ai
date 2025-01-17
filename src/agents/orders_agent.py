from phi.agent import Agent
from phi.model.openai import OpenAIChat
from src.tools.order_manager import OrdersToolkit

orders_agent_instructions = [
    "Welcome to the Sleep Better team! You are responsible for handling order processing tasks efficiently and accurately.",
    
    "IMPORTANT: All your responses must be in JSON format using the following structure:",
    """{
        "answer": "A clear, human-friendly message summarizing the result or action taken.",
        "command": "The specific tool command to execute.",
        "arguments": { 
            "args": { ... Command-specific arguments as key-value pairs ... }
        }
    }""",
    
    "You have access to the following tools for managing orders:",
    "1. **handle_summarize_order_details**: Summarizes the details of an order before creation.",
    "   - Arguments: {args: {product_name, size, price}}",
    "   - Returns: JSON with the output of the function.",
    # "   - Example:",
    # """   {
    #        "answer": "The Ultra Comfort Mattress (Queen) is $1,299. Would you like to proceed?",
    #        "command": "handle_summarize_order_details",
    #        "arguments": {
    #            "args": {
    #                "product_name": "[from context]",
    #                "size": "[from context]",
    #                "price": "[from context]"
    #            }
    #        }
    #     }""",
    
    "2. **handle_create_order**: Creates the final order for processing.",
    "   - Arguments: {args: {product_name, size, price, shipping_address, payment_method}}",
    "   - Returns: JSON with details of the created order.",
    # "   - Example:",
    # """   {
    #        "answer": "Order created successfully.",
    #        "command": "handle_create_order",
    #        "arguments": {
    #            "args": {
    #                "product_name": "[from context]",
    #                "size": "[from context]",
    #                "price": "[from context]",
    #                "shipping_address": "[from context]",
    #                "payment_method": "[from context]"
    #            }
    #        }
    #     }""",
    
    "3. **handle_get_status**: Retrieves the status of an existing order.",
    "   - Arguments: {args: {order_id}}",
    "   - Returns: JSON with the current status of the order.",
    # "   - Example:",
    # """   {
    #        "answer": "Your order is currently being processed.",
    #        "command": "handle_get_status",
    #        "arguments": {
    #            "args": {
    #                "order_id": "[from context]"
    #            }
    #        }
    #     }""",
    
    "Workflow for Processing Orders:",
    "1. Use the context or `product_details_agent` to fetch required information (e.g., product details).",
    "2. Invoke the relevant tool using the correct arguments.",
    "3. Ensure all arguments are encapsulated in a dictionary under the key `args`.",
    "4. Return the JSON response after the tool execution. Ensure the 'command' field reflects the tool called.",
    
    "IMPORTANT: Always prioritize tool execution over formatting responses. The reasoning agent will handle formatting if necessary."
]

def create_sqlite_orders_agent(db_path="/path/to/orders.db", product_details_kb=None):
    orders_toolkit = OrdersToolkit(db_path=db_path)
    return Agent(
        name="Orders Agent",
        agent_id="orders-agent",
        model=OpenAIChat(
            id="gpt-4o",
            response_format={"type": "json_object"}
        ),
        tools=[orders_toolkit],
        knowledge=product_details_kb,
        search_knowledge=True,
        markdown=True,
        read_chat_history=True,
        add_history_to_messages=True,
        instructions=orders_agent_instructions,
        debug_mode=True,
        # show_tool_calls=True,
        description="Order processing specialist for Sleep Better mattresses"
    )