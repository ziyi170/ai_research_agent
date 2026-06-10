"""
ArXiv Search Tool - searches arxiv.org for relevant papers.

Uses the arxiv Python library to fetch paper metadata.
Returns structured results the agent can use for context.
"""

import arxiv
import asyncio
from typing import Optional


async def search_arxiv(
    query: str,
    max_results: int = 5,
    sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance
) -> list[dict]:
    """
    Searches ArXiv for papers matching the query.
    
    Returns list of dicts with: title, abstract, url, authors, published
    Runs the blocking arxiv call in a thread pool to stay async-safe.
    """

    def _search():
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        WITHDRAWN_SIGNALS = [
            "this paper has been withdrawn",
            "this paper has been retracted", 
            "duplicate of arxiv",
            "submitted under a pseudonym",
            "administratively withdrawn"
        ]
        results = []
        for paper in client.results(search):
            abstract_lower = paper.summary.lower()
            title_lower = paper.title.lower()
            # Skip withdrawn or retracted papers
            if any(signal in abstract_lower or signal in title_lower 
                   for signal in WITHDRAWN_SIGNALS):
                continue
            results.append({
                "title": paper.title,
                "abstract": paper.summary[:800],
                "url": paper.entry_id,
                "authors": [a.name for a in paper.authors[:3]],
                "published": str(paper.published.date()),
            })
        # Sort by published date, newest first
        results.sort(key=lambda x: x["published"], reverse=True)
        return results[:max_results]

    # Run blocking IO in thread pool to not block the event loop
    return await asyncio.get_event_loop().run_in_executor(None, _search)
