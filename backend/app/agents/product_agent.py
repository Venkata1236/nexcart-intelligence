import os

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from loguru import logger

from app.core.config import settings
from app.agents.tools import get_recommendations, search_by_sentiment, get_product_detail


# ─────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────

SYSTEM_PROMPT = """You are a helpful product advisor for NexCart — a smart retail platform.

Your job is to help users find the best products using:
- Personalized recommendations based on their purchase history
- Sentiment analysis on product reviews
- Detailed product information

Guidelines:
- Always mention sentiment scores when recommending products
- Flag hidden gems — high quality products with low visibility
- Be concise and specific in your responses
- If a user is new, explain you are showing popular products
- Always use the available tools before answering product questions
"""


# ─────────────────────────────────────────
# AGENT FACTORY
# ─────────────────────────────────────────

def create_product_agent() -> AgentExecutor:
    """
    Create and return a LangChain AgentExecutor with 3 tools.
    Uses Groq Llama 3.1 70B — NOT OpenAI.
    """
    import os
    os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

    llm = ChatGroq(
        model="llama-3.1-70b-versatile",
        temperature=0
    )

    # Tools list
    tools = [
        get_recommendations,
        search_by_sentiment,
        get_product_detail
    ]

    # Prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    # Create agent
    agent = create_openai_functions_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    # Wrap in executor
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