from fastapi import APIRouter, HTTPException
from loguru import logger
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv(override=True)
from app.models.schemas import AgentQueryRequest, AgentQueryResponse
from app.ml.collaborative import collaborative_filter

router = APIRouter()

@router.post("/agent/query", response_model=AgentQueryResponse)
async def agent_query(request: AgentQueryRequest):
    logger.info(f"Agent query — user: {request.user_id}, query: {request.query}")
    try:
        recs = collaborative_filter.get_recommendations(request.user_id, n=5)
        products = [r["product_id"] for r in recs["recommendations"]]

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=os.environ.get("GROQ_API_KEY")
        )

        prompt = f"""You are a NexCart product advisor. 
User query: {request.query}
Available products: {products}
Give a helpful 2-3 sentence response mentioning these product IDs."""

        response = llm.invoke(prompt)
        return AgentQueryResponse(
            response=response.content,
            products_mentioned=products
        )
    except Exception as e:
        logger.error(f"Agent query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))