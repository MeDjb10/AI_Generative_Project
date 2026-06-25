# NutriCoach 🥗🤖
### An AI Nutrition & Health Advisor — a RAG system with a built-in agent

> Module: IA Générative
> This project combines **both** of your project guides into one: the full
> **RAG pipeline** *and* a basic **AI agent** that decides which tool to use.

---

## 0. Read this first

You are building an app where a person types a health or nutrition question, and the
app figures out **how** to answer it. That "figures out how" is the *agent*.

There are three kinds of questions, and the agent sends each to a different place:

| The user asks… | The agent decides… | What runs |
|---|---|---|
| "What foods help lower cholesterol?" | This is *knowledge* | **RAG**: search your health PDFs, then answer |
| "I'm 75 kg, 178 cm, 22 yrs — my daily calories?" | This is *math* | **Internal tool**: a calculator function you write |
| "How much protein is in 100 g of chicken?" | This is a *fact lookup* | **External tool**: the free USDA food API |

After getting the information, the LLM writes a clean final answer.

**Why this is a strong project:** a plain RAG only retrieves and answers. Yours
*reasons* about the question, *chooses* a tool, *shows its reasoning*, and *combines*
the result. That is exactly what the agent guide asks for (internal tool + external
API + orchestration + explained decisions), while still doing the complete RAG pipeline
the RAG guide asks for.

---

## 1. How this maps to your two guides (requirement checklist)

**RAG guide — every step is covered:**
- ✅ Load documents — `ingest.py`
- ✅ Chunking (size + overlap) — `ingest.py`
- ✅ Embeddings — `ingest.py` (sentence-transformers)
- ✅ Vector indexing (ChromaDB) — `ingest.py`
- ✅ Retrieval — `rag.py`
- ✅ Context building + LLM generation — `rag.py` (Groq)

**Agent guide — every requirement is covered:**
- ✅ Understands a natural-language request — the agent reads the question
- ✅ Makes an autonomous decision — `agent.py` picks a route
- ✅ Internal tool (a function) — BMI / calorie calculator in `tools.py`
- ✅ External tool (an API) — USDA food lookup in `tools.py`
- ✅ Orchestration logic — `agent.py`
- ✅ Shows reasoning / explains its decision — the agent prints why it chose a route

This single project satisfies *both* documents. You can present it under either subject.

---

## 2. The architecture

```
                       User question
                            │
                            ▼
                   ┌──────────────────┐
                   │      AGENT       │   asks: "what does this need?"
                   │  (agent.py)      │   → outputs reasoning + a decision
                   └──────────────────┘
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌──────────────┐
        │   RAG    │  │Calculator│  │  USDA  API    │
        │ (PDFs)   │  │(function)│  │ (external)    │
        │ rag.py   │  │ tools.py │  │  tools.py     │
        └──────────┘  └──────────┘  └──────────────┘
              └─────────────┼─────────────┘
                            ▼
                  ┌──────────────────┐
                  │  LLM writes the  │
                  │  final answer    │  (Groq)
                  └──────────────────┘
```

---

## 3. The RAG pipeline explained for a total beginner

Imagine you have 200 pages of health PDFs and someone asks one question. You can't
paste 200 pages into an LLM. So:

1. **Load documents** — read the text out of your PDF files.
2. **Chunking** — cut that text into small pieces (e.g. ~800 characters each), with a
   little **overlap** (e.g. 100 characters) so a sentence isn't sliced in half and
   loses meaning. Each piece is a "chunk".
3. **Embeddings** — turn each chunk into a list of numbers (a "vector") that captures
   its *meaning*. Chunks about similar topics get similar numbers. A small free model
   (`all-MiniLM-L6-v2`) does this on your laptop, no API needed.
4. **Vector indexing** — store all these vectors in a **vector database** (ChromaDB)
   so we can search them fast.
5. **Retrieval** — when a question comes in, we embed the *question* too, then ask the
   database "which chunks are closest in meaning?" It returns the top *k* (e.g. 4)
   most relevant chunks.
6. **Generation** — we paste those chunks into a prompt as "context" and ask the LLM:
   "Using only this context, answer the question." Now the answer is grounded in your
   real documents, not invented.

That's the whole RAG idea: **find the right pages, then let the LLM read them and answer.**

---

## 4. The agent explained for a total beginner

A chatbot just answers. An **agent** first *thinks* about what to do.

In NutriCoach, the agent is one LLM call that returns a small decision like:

```json
{ "action": "calculator", "reasoning": "The user gave weight/height and asked for calories — this is a computation, not a document lookup." }
```

Your code reads that decision and runs the matching path (RAG, calculator, or API).
This is the **orchestration logic**, and because the agent returns its `reasoning`,
you can print it on screen — that's the "explain its decisions" requirement, done.

---

## 5. Tech stack (and why each choice — useful for your report)

| Piece | Choice | Why (beginner-friendly + free) |
|---|---|---|
| Language | **Python** | Required by the guides; you already know the basics |
| LLM | **Groq** (e.g. `llama-3.3-70b-versatile`) | Free, very fast, recommended in the guide |
| Embeddings | **sentence-transformers** `all-MiniLM-L6-v2` | Free, runs locally, no API key |
| Vector DB | **ChromaDB** | Easier for beginners than FAISS, saves to disk automatically |
| PDF reading | **pypdf** | Simple, pure Python |
| External API | **USDA FoodData Central** | Free, real nutrition data, simple key |
| UI (optional) | **Streamlit** | Turns your script into a web page in ~15 lines |

> You can swap ChromaDB for FAISS if your teacher prefers — the guide mentions both.
> ChromaDB is recommended here because it's the gentlest start.

---

## 6. Setup (do this once)

### 6.1 Install Python and create a project folder
```bash
mkdir nutricoach
cd nutricoach
python -m venv venv
# Windows:  venv\Scripts\activate
# Mac/Linux:  source venv/bin/activate
```

### 6.2 Create `requirements.txt`
```
groq
chromadb
sentence-transformers
pypdf
requests
python-dotenv
streamlit
```
Then install:
```bash
pip install -r requirements.txt
```

### 6.3 Get your free API keys
- **Groq** (the LLM): create a free account at console.groq.com → API Keys → create one.
- **USDA** (the food API): get a free key at fdc.nal.usda.gov/api-key-signup.html

Create a file named `.env` in your folder:
```
GROQ_API_KEY=your_groq_key_here
USDA_API_KEY=your_usda_key_here
```
> Never share `.env` or commit it to GitHub.

### 6.4 Final folder structure
```
nutricoach/
├── data/                 # put your health/nutrition PDFs here
├── chroma_db/            # auto-created when you run ingest.py
├── .env                  # your API keys
├── requirements.txt
├── ingest.py             # STEP A: load → chunk → embed → index
├── rag.py                # STEP B: retrieve → generate
├── tools.py              # STEP C: calculator + USDA API
├── agent.py              # STEP D: the decision-maker (orchestration)
├── app.py                # STEP E: run it in the terminal
└── app_streamlit.py      # STEP F (optional): web interface
```

---

## 7. Get your corpus (the "real data" requirement)

Both guides insist on **real documents**. Download 5–15 PDFs about nutrition/health and
drop them in `data/`. Good free, reputable sources:
- World Health Organization (WHO) healthy-diet fact sheets
- National dietary guidelines (e.g. "Dietary Guidelines" PDFs)
- University nutrition course notes / public health handbooks
- Reputable nutrition association guides

Aim for ~30–100 pages total. Quality and relevance matter more than quantity.

---

## 8. Step-by-step implementation (copy each file)

### STEP A — `ingest.py` : load → chunk → embed → index

```python
# ingest.py
# Reads every PDF in data/, splits the text into overlapping chunks,
# turns each chunk into an embedding, and stores them in ChromaDB.

import os
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

DATA_DIR = "data"
CHUNK_SIZE = 800        # characters per chunk  (try 500–1000)
CHUNK_OVERLAP = 100     # characters shared between neighbours

# 1) LOAD: read text from every PDF
def load_documents(folder):
    docs = []
    for filename in os.listdir(folder):
        if filename.lower().endswith(".pdf"):
            path = os.path.join(folder, filename)
            reader = PdfReader(path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
            docs.append({"source": filename, "text": text})
            print(f"Loaded {filename} ({len(text)} characters)")
    return docs

# 2) CHUNK: cut text into overlapping pieces
def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += size - overlap   # step forward, keeping an overlap
    return chunks

def main():
    docs = load_documents(DATA_DIR)

    # 3) EMBEDDINGS: load the free local model
    print("Loading embedding model...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    # 4) INDEX: open (or create) the vector database
    client = chromadb.PersistentClient(path="chroma_db")
    # start fresh each time you re-ingest
    if "nutrition" in [c.name for c in client.list_collections()]:
        client.delete_collection("nutrition")
    collection = client.create_collection("nutrition")

    all_chunks, metadatas, ids = [], [], []
    counter = 0
    for doc in docs:
        for chunk in chunk_text(doc["text"]):
            all_chunks.append(chunk)
            metadatas.append({"source": doc["source"]})
            ids.append(f"chunk_{counter}")
            counter += 1

    print(f"Created {len(all_chunks)} chunks. Embedding...")
    embeddings = embedder.encode(all_chunks, show_progress_bar=True).tolist()

    collection.add(
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )
    print(f"✅ Stored {len(all_chunks)} chunks in ChromaDB.")

if __name__ == "__main__":
    main()
```
Run it: `python ingest.py` (re-run whenever you change your PDFs).

---

### STEP B — `rag.py` : retrieve → build context → generate

```python
# rag.py
# Given a question, find the most relevant chunks and ask the LLM to answer
# using ONLY those chunks.

import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq

load_dotenv()

embedder = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("nutrition")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

def retrieve(question, k=4):
    """Embed the question and return the k closest chunks."""
    q_embedding = embedder.encode([question]).tolist()
    results = collection.query(query_embeddings=q_embedding, n_results=k)
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    return chunks, sources

def answer_with_rag(question):
    chunks, sources = retrieve(question)
    context = "\n\n---\n\n".join(chunks)

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
    answer += f"\n\n📚 Sources: {', '.join(set(sources))}"
    return answer

if __name__ == "__main__":
    print(answer_with_rag("What foods are good for lowering cholesterol?"))
```

---

### STEP C — `tools.py` : internal calculator + external API

```python
# tools.py
# Two tools the agent can call.
#  - calculate_nutrition_needs(): an INTERNAL tool (a pure Python function)
#  - food_lookup():               an EXTERNAL tool (USDA API)

import os
import requests
from dotenv import load_dotenv

load_dotenv()
USDA_API_KEY = os.getenv("USDA_API_KEY")

# ---------- INTERNAL TOOL ----------
def calculate_nutrition_needs(weight_kg, height_cm, age, sex="male", activity="moderate"):
    """BMI + daily calorie needs using the Mifflin-St Jeor formula."""
    # BMI
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 1)

    # BMR
    if sex.lower().startswith("m"):
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    # activity multiplier -> TDEE (total daily calories)
    factors = {"sedentary": 1.2, "light": 1.375,
               "moderate": 1.55, "active": 1.725, "very_active": 1.9}
    tdee = round(bmr * factors.get(activity, 1.55))

    if bmi < 18.5:      category = "underweight"
    elif bmi < 25:      category = "normal weight"
    elif bmi < 30:      category = "overweight"
    else:               category = "obese"

    return {
        "bmi": bmi,
        "bmi_category": category,
        "maintenance_calories": tdee,
        "note": "Estimate using the Mifflin-St Jeor equation.",
    }

# ---------- EXTERNAL TOOL ----------
def food_lookup(food_name):
    """Look up nutrition facts for a food from the USDA database."""
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {"query": food_name, "pageSize": 1, "api_key": USDA_API_KEY}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data.get("foods"):
            return {"error": f"No data found for '{food_name}'."}
        food = data["foods"][0]
        wanted = {"Energy", "Protein", "Total lipid (fat)",
                  "Carbohydrate, by difference"}
        nutrients = {}
        for n in food.get("foodNutrients", []):
            if n.get("nutrientName") in wanted:
                nutrients[n["nutrientName"]] = f'{n.get("value")} {n.get("unitName","").lower()}'
        return {"food": food.get("description", food_name),
                "per_100g": nutrients}
    except Exception as e:
        return {"error": f"API request failed: {e}"}

if __name__ == "__main__":
    print(calculate_nutrition_needs(75, 178, 22, "male", "moderate"))
    print(food_lookup("chicken breast"))
```

---

### STEP D — `agent.py` : the decision-maker (orchestration + reasoning)

```python
# agent.py
# The agent: it READS the question, DECIDES which route to take,
# EXPLAINS why, and RUNS the right tool.

import os, json
from dotenv import load_dotenv
from groq import Groq

from rag import answer_with_rag
from tools import calculate_nutrition_needs, food_lookup

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

DECISION_PROMPT = """You are the routing brain of a nutrition assistant.
Read the user's question and choose ONE action:

- "rag": general nutrition/health knowledge questions (diets, foods for a condition, advice).
- "calculator": the user gives body numbers (weight, height, age) and wants BMI or calorie needs.
- "food_lookup": the user asks for nutrition facts of a specific food (calories/protein/etc).
- "direct": small talk or anything the others don't fit.

For "calculator" also extract: weight_kg, height_cm, age, sex (male/female), activity (sedentary/light/moderate/active/very_active).
For "food_lookup" also extract: food_name.

Reply with ONLY valid JSON, no extra text. Examples:
{"action":"rag","reasoning":"..."}
{"action":"calculator","reasoning":"...","weight_kg":75,"height_cm":178,"age":22,"sex":"male","activity":"moderate"}
{"action":"food_lookup","reasoning":"...","food_name":"banana"}

User question: """

def decide(question):
    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": DECISION_PROMPT + question}],
    )
    raw = response.choices[0].message.content.strip()
    # be defensive: pull out the JSON part
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except Exception:
        return {"action": "rag", "reasoning": "Could not parse decision, defaulting to RAG."}

def run(question):
    decision = decide(question)
    action = decision.get("action", "rag")
    print(f"\n🧠 Agent reasoning: {decision.get('reasoning','(none)')}")
    print(f"➡️  Chosen action: {action}\n")

    if action == "calculator":
        result = calculate_nutrition_needs(
            decision.get("weight_kg"), decision.get("height_cm"),
            decision.get("age"), decision.get("sex", "male"),
            decision.get("activity", "moderate"),
        )
        return _phrase(question, result)

    if action == "food_lookup":
        result = food_lookup(decision.get("food_name", question))
        return _phrase(question, result)

    if action == "direct":
        resp = groq_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": question}],
        )
        return resp.choices[0].message.content

    # default: RAG
    return answer_with_rag(question)

def _phrase(question, tool_result):
    """Let the LLM turn raw tool output into a friendly answer."""
    prompt = f"""The user asked: "{question}"
A tool returned this data: {tool_result}
Write a clear, friendly answer based on this data.
Add a short reminder that this is general info, not medical advice."""
    resp = groq_client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": prompt}])
    return resp.choices[0].message.content

if __name__ == "__main__":
    print(run("I'm 75kg, 178cm, 22 years old male, moderately active. My daily calories?"))
```

---

### STEP E — `app.py` : run it in the terminal

```python
# app.py — simple chat loop in the terminal
from agent import run

print("🥗 NutriCoach — ask me about nutrition & health. Type 'quit' to exit.\n")
while True:
    question = input("You: ")
    if question.lower() in ("quit", "exit"):
        break
    answer = run(question)
    print(f"\nNutriCoach: {answer}\n")
```
Run the whole thing:
```bash
python ingest.py     # once, to build the index
python app.py        # chat with it
```

---

### STEP F (optional but impressive) — `app_streamlit.py` : a web UI

```python
# app_streamlit.py
import streamlit as st
from agent import run

st.title("🥗 NutriCoach")
st.caption("AI nutrition advisor — RAG + agent. General info, not medical advice.")

question = st.text_input("Ask a nutrition or health question:")
if st.button("Ask") and question:
    with st.spinner("Thinking..."):
        st.write(run(question))
```
Run it: `streamlit run app_streamlit.py`

---

## 9. Demo script (use these 3 questions in your oral presentation)

Showing all three routes live is what makes the demo shine:

1. **RAG route:** *"What foods help reduce high blood pressure?"*
   → watch it retrieve from your PDFs and cite sources.
2. **Calculator route:** *"I'm 68 kg, 170 cm, 25, female, lightly active — my daily calories?"*
   → watch the agent choose the internal tool.
3. **API route:** *"How much protein is in 100 g of lentils?"*
   → watch it call the USDA API live.

Point out the printed **"Agent reasoning"** each time — that's your "explained decisions".

---

## 10. Mapping to the required REPORT structure

| Report section | What to write |
|---|---|
| Introduction | The problem: people need quick, grounded nutrition answers |
| Objective | Build a RAG system + a basic agent for nutrition Q&A |
| System description | The 3 routes (RAG / calculator / API) and when each is used |
| RAG pipeline | Explain load → chunk → embed → index → retrieve → generate (Section 3 of this README, in your words) |
| Architecture | Use the diagram in Section 2 |
| Implementation | Walk through the 6 files; show the chunking + the agent decision |
| Results & tests | The 3 demo questions + screenshots; what worked / failed |
| Link with course concepts | Embeddings, vector DB, retrieval, tools, orchestration, MCP idea |
| Limits & improvements | See Section 12 |
| Conclusion | What you learned |

---

## 11. Mapping to the SÉANCE deliverables

| Séance | Deliverable | What to show |
|---|---|---|
| Launch | 1-page description + pipeline schema + corpus | The idea above + the diagram + your chosen PDFs |
| Validation 1 | Load + chunk + embed working | `ingest.py` running, print chunk count |
| Validation 2 | Vector DB + retriever working | `rag.py` `retrieve()` returning relevant chunks (test top-k) |
| Validation 3 | Full RAG pipeline | `answer_with_rag()` answering from docs |
| Final | Full system + report + demo | Add `agent.py` + `tools.py` (the agent layer) + Streamlit |

> Tip: build it **in this exact order**. Don't add the agent until plain RAG works.

---

## 12. How to make it even better (bonus points, mentioned in the guides)

- **Try different chunk sizes / overlap** (500 vs 1000) and report which retrieved better.
- **Compare ChromaDB vs FAISS** and write 2 lines on the difference.
- **Tune top-k** (3 vs 6) and observe answer quality.
- **Conversational memory:** keep a list of past messages and pass them to the LLM.
- **Re-ranking:** retrieve 10 chunks, then ask the LLM to pick the best 4.
- **Error handling:** the API tool already handles failures — mention this (the agent guide asks for it).
- **MCP idea:** explain that your structured `{action, reasoning, args}` decision is the
  same principle as the Model Context Protocol — structuring context for tools.

---

## 13. Common beginner errors & fixes

| Problem | Fix |
|---|---|
| `collection not found` | Run `python ingest.py` first |
| Empty/garbled PDF text | Some PDFs are scanned images; use text-based PDFs |
| Groq model error | Model names change — check console.groq.com for the current one |
| USDA returns nothing | Check your `USDA_API_KEY` in `.env` |
| Slow first run | The embedding model downloads once (~80 MB), then it's fast |
| `ModuleNotFoundError` | Activate your venv, re-run `pip install -r requirements.txt` |

---

## 14. Mini glossary

- **Chunk:** a small piece of a document.
- **Embedding:** a list of numbers that represents the *meaning* of text.
- **Vector database:** storage that finds items with similar meaning fast.
- **Retrieval:** fetching the most relevant chunks for a question.
- **LLM:** the large language model that writes the final answer (here, via Groq).
- **Agent:** code that decides *what to do* before answering, not just answers.
- **Tool:** a function or API the agent can call (calculator, USDA lookup).
- **Orchestration:** the logic that routes the question to the right tool.

---

*Disclaimer for your app: NutriCoach gives general educational information, not medical advice.*
```
