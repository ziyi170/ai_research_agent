"""
API Routes - handles incoming requests and orchestrates agent responses
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from agent.planner import AgentPlanner
from agent.memory import ConversationMemory

router = APIRouter()
memory = ConversationMemory()
planner = AgentPlanner()


class QueryRequest(BaseModel):
    query: str
    session_id: str = "default"
    top_k: Optional[int] = 3


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    steps_taken: list[str]
    session_id: str


@router.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """
    Main query endpoint. Accepts user question, runs agent pipeline,
    returns answer with sources and reasoning steps.
    """
    try:
        # Retrieve conversation history for this session
        history = memory.get_history(request.session_id)

        # Agent plans and executes
        result = await planner.run(
            query=request.query,
            history=history,
            top_k=request.top_k
        )

        # Save turn to memory
        memory.add_turn(
            session_id=request.session_id,
            user_msg=request.query,
            assistant_msg=result["answer"]
        )

        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            steps_taken=result["steps"],
            session_id=request.session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """Returns conversation history for a given session."""
    return {"history": memory.get_history(session_id)}


@router.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """Clears conversation history for a session."""
    memory.clear(session_id)
    return {"message": "History cleared"}


@router.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
