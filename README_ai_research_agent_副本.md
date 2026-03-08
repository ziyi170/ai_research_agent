# 🔍 AI Research Agent

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=flat&logo=openai&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-blue?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

An intelligent research assistant that answers questions about academic papers using **Retrieval-Augmented Generation (RAG)** and an **agentic planning layer**. Ask a question — the agent decides whether to search arXiv, retrieve from a local vector index, or query the LLM directly, then returns a grounded answer with cited sources.

---

## ✨ Features

- **Agentic planning** — query intent classification routes requests to the right tools automatically
- **RAG pipeline** — overlapping text chunking → OpenAI embeddings → FAISS semantic search → context-injected generation
- **arXiv integration** — searches live academic papers and surfaces relevant abstracts
- **Multi-turn memory** — session-based sliding-window conversation history across requests
- **Async throughout** — non-blocking FastAPI backend handles concurrent requests
- **Structured responses** — every answer includes sources and agent reasoning steps

---

## 🏗 Architecture

```
user query
    ↓
FastAPI backend        (async REST API, Pydantic-validated schemas)
    ↓
Agent Planner          (intent classification → tool sequence)
    ↓
Tool Execution
  ├── arXiv Search     (live paper search via arxiv API)
  ├── FAISS Retrieval  (semantic search over local vector index)
  └── LLM Summariser   (context-injected GPT-4o-mini generation)
    ↓
structured response    { answer, sources, steps_taken, session_id }
```

---

## 📁 Project Structure

```
backend/
├── main.py                  # FastAPI app entry point + CORS
├── api/
│   └── routes.py            # REST endpoints: /query /history
├── agent/
│   ├── planner.py           # Core agent: tool selection + orchestration
│   └── memory.py            # Session-based sliding-window memory
├── tools/
│   ├── arxiv_search.py      # Async arXiv paper search
│   └── summariser.py        # LLM-based summarisation prompt
├── retrieval/
│   ├── chunking.py          # Overlapping text chunking (512 chars, 64 overlap)
│   ├── vector_store.py      # FAISS IndexFlatIP with L2 normalisation
│   └── retriever.py         # Embed → search → return top-k chunks
└── llm/
    └── client.py            # OpenAI wrapper (chat + embeddings)
```

---

## ⚙️ Key Technical Decisions

| Decision | Rationale |
|---|---|
| **FAISS IndexFlatIP** | Sub-millisecond search, no external DB dependency; vectors L2-normalised for cosine similarity |
| **Overlapping chunks** | 64-char overlap prevents context loss at chunk boundaries |
| **Sliding-window memory** | Caps history at N turns to stay within LLM context limit without truncating mid-conversation |
| **Async throughout** | `async/await` + `asyncio.gather` for parallel embedding calls; never blocks the event loop |
| **Tool registry pattern** | `TOOL_REGISTRY` dict maps names → functions; adding a new tool is a one-line change |
| **temperature=0.2** | Low temperature for factual Q&A — reduces hallucination while preserving coherent output |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key

### Installation

```bash
# 1. Clone
git clone https://github.com/ziyi170/ai_research_agent
cd ai_research_agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 4. Run
cd backend
uvicorn main:app --reload
# API available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

---

## 📡 API Reference

### POST `/api/query` — Ask a question

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are recent advances in RAG for LLMs?",
    "session_id": "user123",
    "top_k": 3
  }'
```

**Response:**
```json
{
  "answer": "Recent advances in RAG include...",
  "sources": ["https://arxiv.org/abs/2312.10997"],
  "steps_taken": ["search_arxiv", "retrieve_docs", "summarise"],
  "session_id": "user123"
}
```

### GET `/api/history/{session_id}` — Retrieve conversation history

```bash
curl http://localhost:8000/api/history/user123
```

### DELETE `/api/history/{session_id}` — Clear session

```bash
curl -X DELETE http://localhost:8000/api/history/user123
```

### GET `/api/health` — Health check

```bash
curl http://localhost:8000/api/health
# {"status": "ok", "version": "1.0.0"}
```

---

## 🧠 How the Agent Works

The `AgentPlanner` uses **intent classification** to decide which tools to run:

```python
# Query contains "paper", "research", "arxiv"
→ ["search_arxiv", "retrieve_docs", "summarise"]

# Query contains "document", "find", "retrieve"
→ ["retrieve_docs", "summarise"]

# General knowledge question
→ ["llm_answer"]
```

This is a rule-based implementation. Production systems would replace this with **LLM function calling** or a **ReAct** (Reason + Act) prompting pattern for dynamic tool selection.

---

## 🗺 Roadmap

- [ ] Re-ranking with a cross-encoder model (improve retrieval precision)
- [ ] Hybrid search — BM25 + dense retrieval combined
- [ ] RAGAS evaluation pipeline (faithfulness, answer relevance metrics)
- [ ] Redis-backed session memory (horizontal scaling)
- [ ] Streaming responses via SSE
- [ ] LangGraph-based multi-agent architecture (planner + researcher + writer)

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI + Pydantic |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small (1536-dim) |
| Vector Search | FAISS (IndexFlatIP) |
| Paper Search | arXiv API |
| Runtime | Python 3.11, asyncio |

---

## 📄 License

MIT
