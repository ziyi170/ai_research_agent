"""
Summariser - uses LLM to generate concise summaries of retrieved content.
Separate from the main LLM client so summarisation prompts can be tuned independently.
"""

from llm.client import call_llm


async def summarise_with_llm(texts: list[str], query: str) -> str:
    """
    Summarises a list of text passages in the context of the user query.
    
    Args:
        texts: list of document chunk strings
        query: the original user question
    
    Returns:
        concise summary string
    """
    combined = "\n\n---\n\n".join(texts[:5])  # Cap at 5 passages to control tokens

    prompt = f"""Summarise the following research content to answer this question:
"{query}"

Content:
{combined}

Provide a concise, accurate summary. Include key findings and cite specific claims."""

    return await call_llm(query=prompt, context="")
