"""
Agent Planner - decides which tools to use based on user query,
then orchestrates execution and final LLM response generation.

This is the core "brain" of the agent system.
"""

import asyncio
from tools.arxiv_search import search_arxiv
from retrieval.retriever import index_documents
from tools.summariser import summarise_with_llm
from retrieval.retriever import retrieve_docs
from llm.client import call_llm
from typing import Optional


TOOL_REGISTRY = {
    "search_arxiv": search_arxiv,
    "retrieve_docs": retrieve_docs,
    "summarise": summarise_with_llm,
    "llm_answer": call_llm,
}


class AgentPlanner:
    """
    Rule-based + LLM-assisted planner.
    
    For a real system you'd replace rule-based routing with an LLM that
    generates a structured plan (ReAct / function calling pattern).
    """

    def _plan(self, query: str) -> list[str]:
        """
        Determines execution plan based on query content.
        Returns ordered list of tool names to execute.
        """
        query_lower = query.lower()

        # Follow-up intent — use memory, don't re-search
        if any(kw in query_lower for kw in ["second", "third", "first", "elaborate", "tell me more", "expand", "previous", "last", "that paper"]):
            return ["llm_answer"]

        # Research / paper intent
        if any(kw in query_lower for kw in ["paper", "research", "arxiv", "study", "author"]):
            return ["search_arxiv", "retrieve_docs", "summarise"]

        # Document retrieval intent
        if any(kw in query_lower for kw in ["document", "article", "find", "retrieve"]):
            return ["retrieve_docs", "summarise"]

        # Default: direct LLM answer
        return ["llm_answer"]

    async def run(
        self,
        query: str,
        history: list[dict],
        top_k: int = 3
    ) -> dict:
        """
        Main agent loop:
        1. Plan tool sequence
        2. Execute each tool
        3. Aggregate results
        4. Generate final LLM response
        """
        plan = self._plan(query)
        steps_taken = []
        context_chunks = []
        sources = []

        for tool_name in plan:
            steps_taken.append(tool_name)

            if tool_name == "search_arxiv":
                search_query = f"{query} research paper"
                results = await search_arxiv(search_query)
                sources.extend([r["url"] for r in results])
                context_chunks.extend([r["abstract"] for r in results])
                await index_documents([
                    {"text": r["abstract"], "source": r["url"]}
                    for r in results
                ])

            elif tool_name == "retrieve_docs":
                results = await retrieve_docs(query, top_k=top_k)
                sources.extend([r["source"] for r in results])
                context_chunks.extend([r["text"] for r in results])

            elif tool_name in ("summarise", "llm_answer"):
                # Final step: generate answer from accumulated context
                answer = await call_llm(
                    query=query,
                    context="\n\n".join(context_chunks),
                    history=history
                )
                return {
                    "answer": answer,
                    "sources": list(dict.fromkeys(sources)),
                    "steps": steps_taken,
                    "abstracts": context_chunks
                }

        # Fallback if plan didn't include a generation step
        # Extract paper references from history to use as context
        print("DEBUG history length:", len(history))
        print("DEBUG history contents:", [m.get("content","")[:100] for m in history])
        paper_context = ""
        for msg in history:
            if "[Papers referenced:" in msg.get("content", ""):
                paper_context = msg["content"].split("[Papers referenced:")[-1].rstrip("]")
        answer = await call_llm(query=query, context=paper_context, history=history)
        return {"answer": answer, "sources": [], "steps": steps_taken}
