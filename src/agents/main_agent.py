import json
import os
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.embedder.openai import OpenAIEmbedder
from phi.knowledge.pdf import PDFKnowledgeBase, PDFReader
from phi.storage.agent.postgres import PgAgentStorage
from phi.vectordb.pgvector import PgVector, SearchType
from phi.playground import Playground, serve_playground_app
from src.agents.orders_agent import create_sqlite_orders_agent
from src.agents.reasoning_agent import get_reasoning_agent
from src.agents.product_agents import create_product_details_agent, create_product_reviews_agent
# Load settings
settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'settings.json')

with open(settings_path) as f:
    settings = json.load(f) 

print(settings)

db_url = settings["database"]["url"]
collections = settings["database"]["collections"]
product_details_data_path = settings["data"]["product_catalog"]
product_reviews_data_path = settings["data"]["product_reviews"]

# Vector Databases
product_details_vector_db = PgVector(
    table_name=collections["product_details"],
    db_url=db_url,
    search_type=SearchType.hybrid,
    embedder=OpenAIEmbedder(model="text-embedding-3-small"),
)

product_reviews_vector_db = PgVector(
    table_name=collections["product_reviews"],
    db_url=db_url,
    search_type=SearchType.hybrid,
    embedder=OpenAIEmbedder(model="text-embedding-3-small"),
)

# Knowledge Bases
product_details_kb = PDFKnowledgeBase(
    path=product_details_data_path,
    vector_db=product_details_vector_db,
    reader=PDFReader(chunk=True)
)

product_reviews_kb = PDFKnowledgeBase(
    path=product_reviews_data_path,
    vector_db=product_reviews_vector_db,
    reader=PDFReader(chunk=True)
)

# Load Knowledge Bases
product_details_kb.load(upsert=True)
product_reviews_kb.load(upsert=True)

enabled_agents = []
# Sub-Agents

if settings['agents']['product_details']['enabled']:
    product_details_agent = create_product_details_agent(product_details_kb, db_url)
    enabled_agents.append(product_details_agent)
    
if settings['agents']['product_reviews']['enabled']:
    product_reviews_agent = create_product_reviews_agent(product_reviews_kb, db_url)
    enabled_agents.append(product_reviews_agent)
    
if settings['agents']['orders']['enabled']:
    orders_agent = create_sqlite_orders_agent(db_path=settings["database"]["orders_path"], product_details_kb=product_details_kb)
    enabled_agents.append(orders_agent)


reasoning_agent = get_reasoning_agent(enabled_agents)

# Playground App
# app = Playground(agents=[reasoning_agent]).get_app()

# if __name__ == "__main__":
#     serve_playground_app("frodo_agents:app", reload=True)