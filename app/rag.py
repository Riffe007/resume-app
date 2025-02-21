import asyncio
import os
import json
import httpx  # Using httpx for async API calls

# Load environment variables
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")  
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")  # Consistent naming
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")  # Using vector store, not AI Search

async def retrieve_context(query: str) -> str:
    """
    Retrieve relevant context from the vector store.
    """
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_KEY or not VECTOR_STORE_ID:
        raise ValueError("❌ Missing required Azure OpenAI or Vector Store environment variables!")

    search_url = f"{AZURE_OPENAI_ENDPOINT}/vectorstores/{VECTOR_STORE_ID}/search"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY
    }
    
    payload = {
        "query": query,
        "top_k": 5  # Retrieve top 5 relevant vector results
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(search_url, headers=headers, json=payload)
        data = response.json()

    # Extract relevant content from response
    if "matches" in data:
        return "\n".join([match["text"] for match in data["matches"]])
    else:
        return "No relevant context found."

def apply_guardrails(text: str) -> str:
    """
    Apply guardrails to filter sensitive content, enforce rules, and ensure quality.
    """
    # Example: Removing explicit content or PII (This is a simple dummy example)
    restricted_words = ["classified", "confidential", "restricted"]
    for word in restricted_words:
        text = text.replace(word, "[REDACTED]")
    
    return text

async def generate_rag_prompt(user_prompt: str) -> str:
    """
    Retrieve additional context using the vector store and apply guardrails before returning the final prompt.
    """
    context = await retrieve_context(user_prompt)
    combined_prompt = f"{user_prompt}\n\n🔎 Additional Context:\n{context}"
    final_prompt = apply_guardrails(combined_prompt)
    return final_prompt
