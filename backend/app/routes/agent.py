from fastapi import APIRouter, HTTPException
from loguru import logger

from app.models.schemas import AgentQueryRequest, AgentQueryResponse
from app.agents.product_agent import get_agent, extract_product_ids

router = APIRouter()


@router.post("/agent/query", response_model=AgentQueryResponse)
async def agent_query(request: AgentQueryRequest):
    """
    Natural language product search via LangChain agent.

    - Input:  user_id + natural language query
    - Output: agent response + product IDs mentioned
    """
    logger.info(f"Agent query — user: {request.user_id}, query: {request.query}")

    try:
        agent = get_agent()

        # Inject user_id into query so agent can call recommendation tool
        enriched_query = f"User ID: {request.user_id}\nQuery: {request.query}"

        result = await agent.ainvoke({"input": enriched_query})
        response_text = result.get("output", "")

        # Extract any product IDs mentioned in response
        products_mentioned = extract_product_ids(response_text)

        logger.info(f"Agent response generated — {len(products_mentioned)} products mentioned")

        return AgentQueryResponse(
            response=response_text,
            products_mentioned=products_mentioned
        )

    except Exception as e:
        logger.error(f"Agent query failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Agent query failed: {str(e)}"
        )