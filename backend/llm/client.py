"""
LLM Client - thin wrapper around OpenAI API.

Keeps prompt construction and API calls in one place so swapping
models (GPT-4, Claude, Gemini) only requires editing this file.
"""

import os
from dotenv import load_dotenv
load_dotenv()
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")

SYSTEM_PROMPT = """You are a helpful AI research assistant.
When given context from retrieved documents, use it to answer the user's question accurately.
If the user refers to a paper by number (e.g. "second paper"), look in the conversation history for [Papers referenced] and use that information to answer.
If the context doesn't contain the answer, say so clearly.
Always be concise and cite the source when possible."""


async def call_llm(
    query: str,
    context: str = "",
    history: list[dict] = None,
    model: str = "gpt-4o-mini"
) -> str:
    """
    Calls the OpenAI chat completion endpoint.
    
    Constructs a messages array with:
    - system prompt
    - conversation history (for multi-turn support)
    - current user query with optional retrieved context
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Inject previous turns for multi-turn dialogue
    if history:
        messages.extend(history)

    # Inject retrieved context into user message
    if context:
        user_content = f"""Context from retrieved documents:
{context}

User question: {query}"""
    else:
        user_content = query

    messages.append({"role": "user", "content": user_content})

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,  # Lower temp = more factual, less creative
        max_tokens=1000
    )

    return response.choices[0].message.content
