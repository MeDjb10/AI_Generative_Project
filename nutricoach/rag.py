# rag.py — STEP B: retrieve → build context → generate
#
# Two halves you can test independently:
#   1) retrieve(question)        -> finds the most relevant chunks (NO LLM needed)
#   2) answer_with_rag(question) -> feeds those chunks to the LLM for a grounded answer
#
# Run modes (see bottom of file):
#   python rag.py                -> full RAG answer (needs GROQ_API_KEY)
#   python rag.py --retrieve     -> ONLY show retrieved chunks (no API key needed)

import os
import sys

# Windows terminals default to cp1252, which can't print emoji (📚, 🥗, ...).
# Force UTF-8 so our output never crashes with UnicodeEncodeError.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq

load_dotenv()  # reads GROQ_API_KEY from your .env

# --- Load the SAME embedding model you used in ingest.py ---
# This is critical: the question must be turned into a vector the *same way*
# the chunks were, or "closeness" comparisons would be meaningless.
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# --- Open the vector DB that ingest.py built ---
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("nutrition")  # errors if you haven't run ingest.py

# --- LLM client (Groq) ---
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def retrieve(question, k=4):
    """Embed the question and return the k closest chunks from the DB.

    Returns (chunks, sources, distances) so you can SEE how good each match is.
    Lower distance = closer in meaning. This needs NO LLM and NO API key.
    """
    q_embedding = embedder.encode([question]).tolist()
    results = collection.query(query_embeddings=q_embedding, n_results=k)

    # ChromaDB returns lists-of-lists (one inner list per query). We sent 1 query,
    # so we take index [0] of each.
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    distances = results["distances"][0]
    return chunks, sources, distances


def answer_with_rag(question, k=4):
    """Full RAG: retrieve the best chunks, then ask the LLM to answer using ONLY them."""
    chunks, sources, _ = retrieve(question, k=k)

    # "Context building": glue the chunks together with clear separators.
    context = "\n\n---\n\n".join(chunks)

    # The prompt is where RAG happens: we ORDER the model to use only our context.
    # This is what keeps the answer grounded in your real PDFs instead of invented.
    prompt = f"""You are a careful nutrition assistant.
Answer the question using ONLY the context below.
If the answer is not in the context, say you don't have that information.

CONTEXT:
{context}

QUESTION: {question}

Answer clearly and mention that this is general information, not medical advice."""

    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    answer = response.choices[0].message.content

    # Cite which documents the answer came from (set() removes duplicates).
    answer += f"\n\n📚 Sources: {', '.join(set(sources))}"
    return answer


if __name__ == "__main__":
    import sys

    question = "What's the best way to lose weight?"

    # STAGE 1: retrieval only — prove your search works before touching the LLM.
    if "--retrieve" in sys.argv:
        chunks, sources, distances = retrieve(question)
        print(f"Question: {question}\n")
        print(f"Top {len(chunks)} chunks (lower distance = more relevant):\n")
        for i, (chunk, source, dist) in enumerate(zip(chunks, sources, distances), 1):
            print(f"[{i}] distance={dist:.3f}  source={source}")
            print(f"    {chunk[:200].strip()}...\n")
    # STAGE 2: full RAG answer.
    else:
        print(answer_with_rag(question))
