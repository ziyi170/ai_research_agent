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
    top_k: Optional[int] = 8


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

        # Save turn to memory (include sources so follow-up questions have context)
        assistant_with_sources = result["answer"]
        if result["sources"]:
            pairs = list(zip(result["sources"], result.get("abstracts", [])))
            if pairs:
                abstract_text = "\n".join(
                    f"Paper {i+1} ({url}):\n{abstract[:200]}..."
                    for i, (url, abstract) in enumerate(pairs)
                )
                assistant_with_sources += f"\n\n[Papers referenced:\n{abstract_text}]"
            else:
                assistant_with_sources += f"\n\n[Sources: {', '.join(result['sources'])}]"

        memory.add_turn(
            session_id=request.session_id,
            user_msg=request.query,
            assistant_msg=assistant_with_sources
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
