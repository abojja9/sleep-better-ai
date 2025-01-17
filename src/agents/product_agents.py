from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.storage.agent.postgres import PgAgentStorage

# Product Details Agent Instructions
product_details_instructions = [
    "Keep responses conversational and concise",
    "Focus on 2-3 key features most relevant to the customer",
    "Use natural comparisons instead of lists",
    "Ask follow-up questions to understand needs",
    "Break down complex information into simple terms",
    "Compare products based on customer's main concerns"
]

product_details_guidelines = [
    "Focus on customer's specific needs",
    "Avoid technical jargon",
    "Keep comparisons simple and relevant"
]

# Reviews Agent Instructions
reviews_agent_instructions = [
    "Highlight 2-3 most relevant reviews",
    "Summarize general customer sentiment",
    "Focus on reviews matching customer's interests",
    "Keep review summaries brief and relevant",
    "Include mix of positive and critical feedback",
    "Only show verified purchase reviews"
]

reviews_agent_guidelines = [
    "Prioritize recent reviews",
    "Balance positive and negative feedback",
    "Focus on specific customer concerns"
]

def create_product_details_agent(knowledge_base, db_url):
    return Agent(
        name="Product Details Agent",
        agent_id="product-details-agent",
        model=OpenAIChat(id="gpt-4o"),
        search_knowledge=True,
        knowledge=knowledge_base,
        storage=PgAgentStorage(table_name="product_details_sessions", db_url=db_url),
        instructions=product_details_instructions,
        guidelines=product_details_guidelines,
        description="Sleep consultant focusing on product features and comparisons",
        system_prompt="""You are part of the Sleep Better team, focusing on product specifications and comparisons.
        Keep your responses:
        - Short and natural
        - Focused on 2-3 key points
        - Relevant to customer needs
        - Conversational with follow-up questions""",
        markdown=True,
        parse_response=True,
        read_chat_history=True,
        add_history_to_messages=True
    )

def create_product_reviews_agent(knowledge_base, db_url):
    return Agent(
        name="Product Reviews Agent",
        agent_id="product-reviews-agent",
        model=OpenAIChat(id="gpt-4o"),
        search_knowledge=True,
        knowledge=knowledge_base,
        storage=PgAgentStorage(table_name="product_reviews_sessions", db_url=db_url),
        instructions=reviews_agent_instructions,
        guidelines=reviews_agent_guidelines,
        description="Sleep consultant focusing on customer feedback and experiences",
        system_prompt="""You are part of the Sleep Better team, handling customer reviews and feedback.
        Keep your responses:
        - Focused on relevant reviews
        - Brief and insightful
        - Balanced in feedback
        - Natural and helpful""",
        markdown=True,
        parse_response=True,
        read_chat_history=True,
        add_history_to_messages=True
    )