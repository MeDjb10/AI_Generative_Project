# Project Description — NutriCoach
### A RAG-based AI Nutrition & Health Advisor
**Module:** IA Générative — Launch séance deliverable

---

## Project description
NutriCoach is an intelligent assistant that answers nutrition and health questions
based on a corpus of **real, reputable health documents** (WHO guidelines, dietary
guidelines, and an open nutrition textbook). Unlike a simple chatbot, NutriCoach does
not invent answers: it retrieves the most relevant passages from these documents and
uses a Large Language Model (LLM) to generate a clear, grounded, contextualized response.

The core of the project is a complete **Retrieval-Augmented Generation (RAG)** pipeline.
In a later phase, a basic **agent** layer is added so the system can also decide, on its
own, when a question needs a calculation (e.g. daily calorie needs) or an external data
lookup (e.g. a food's nutrition facts) instead of document retrieval.

## Use case
A user asks a natural-language question such as *"What foods help reduce high blood
pressure?"* NutriCoach searches its document corpus, finds the most relevant passages,
and produces an accurate answer with its sources cited. The target users are students
and individuals who want reliable, general nutrition information (not medical advice).

## Corpus
A focused set of **6–10 text-based PDF documents (~40–100 pages total)** from trusted
public-health sources:
- "Human Nutrition" open textbook (broad foundation)
- WHO fact sheets and guidelines (healthy diet, sugars, sodium)
- USDA Dietary Guidelines (selected chapters)
- NHS Eatwell Guide, EFSA reference values, Harvard Healthy Eating Plate

The corpus is kept thematically coherent to maximize retrieval relevance.

## RAG pipeline (simple schema)

```
   PDF documents (corpus)
            │
            ▼
   1. Document loading        → read text from PDFs
            │
            ▼
   2. Chunking                → split into ~800-char pieces (100 overlap)
            │
            ▼
   3. Embeddings              → convert each chunk into a meaning-vector
            │
            ▼
   4. Vector indexing         → store vectors in ChromaDB
            │
            ▼
   5. Retrieval               → find top-k chunks closest to the question
            │
            ▼
   6. Generation (LLM)        → build context + prompt → grounded answer
            │
            ▼
   Answer + cited sources
```

## Technologies
- **Python** — main language
- **pypdf** — document loading
- **sentence-transformers** (`all-MiniLM-L6-v2`) — embeddings (free, local)
- **ChromaDB** — vector database / indexing
- **Groq** (`llama-3.3-70b-versatile`) — LLM for generation
- *(Later phase)* internal calculator function + USDA FoodData Central API + a simple
  agent for orchestration; optional Streamlit interface

## Objectives
- Implement and understand the complete RAG pipeline end-to-end
- Work with embeddings, vector search, and an LLM API on real data
- Extend the system with a basic agent that reasons about which tool to use
- Deliver a working system, a report, and a live demonstration

*Note: NutriCoach provides general educational information, not medical advice.*
