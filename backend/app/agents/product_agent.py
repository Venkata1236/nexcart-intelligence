import os

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from loguru import logger

from app.core.config import settings
from app.agents.tools import get_recommendations, search_by_sentiment, get_product_detail

from dotenv import load_dotenv
import os

load_dotenv(
    dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
    override=True
)

# ─────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────

SYSTEM_PROMPT = """You are a helpful product advisor for NexCart.

When a user asks about products, you MUST use the available tools to get real data.
ALWAYS call get_recommendations first to get product suggestions.
Then use get_product_detail to get sentiment for specific products.

Never respond without using at least one tool first.
Always mention product IDs and sentiment scores in your response."""


# ─────────────────────────────────────────
# AGENT FACTORY
# ─────────────────────────────────────────

def create_product_agent() -> AgentExecutor:
    llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.environ.get("GROQ_API_KEY")
)

    tools = [
        get_recommendations,
        search_by_sentiment,
        get_product_detail
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    agent = create_openai_functions_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True
    )

    logger.info("Product agent created ✅ — Groq Llama 3.1 70B")
    return agent_executor


def extract_product_ids(response: str) -> list[str]:
    """
    Extract product IDs mentioned in agent response.
    Product IDs in Amazon dataset are alphanumeric like B001E4KFG0
    """
    import re
    pattern = r'\b[A-Z0-9]{10}\b'
    return list(set(re.findall(pattern, response)))


# Singleton agent — created once at startup
product_agent: AgentExecutor | None = None


def get_agent() -> AgentExecutor:
    """Get or create the singleton agent"""
    global product_agent
    if product_agent is None:
        product_agent = create_product_agent()
    return product_agent