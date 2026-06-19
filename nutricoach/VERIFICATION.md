# How Step A & Step B Were Verified

This file documents the **exact commands** used to verify that the RAG pipeline
works, and how to read the output. Everything is run with the project's
virtual-environment Python: `./venv/Scripts/python.exe` (so the right packages
are used).

> Tip: on Windows PowerShell, replace `./venv/Scripts/python.exe` with
> `.\venv\Scripts\python.exe` if the forward slashes give you trouble.

---

## 0. Pre-check — is the vector DB actually populated? (Step A)

After running `python ingest.py`, we confirmed the chunks really landed in
ChromaDB using `inspect_db.py`.

**Command** (run from inside the `nutricoach/` folder):

```bash
./venv/Scripts/python.exe inspect_db.py
```

**What we looked for in the output:**

- `Total chunks stored: 5378` → the DB is not empty.
- Each chunk shows `Vector: length=384` → the embedding model
  `all-MiniLM-L6-v2` produces 384-dimensional vectors. Seeing 384 confirms the
  embeddings were stored correctly (a wrong/empty value here would mean ingest
  failed).
- Each chunk shows a `Source:` (e.g. `Carbohydrate_intake_WHO.pdf`) → metadata
  was attached, so we can cite sources later.

**Verdict:** Step A (load → chunk → embed → index) confirmed working.

---

## 1. Verify RETRIEVAL only (Step B, stage 1 — no LLM, no API key needed)

The point of this stage is to prove that *semantic search* works **before**
involving the LLM. If retrieval is bad, the final answer can't be good.

`rag.py` has a special `--retrieve` mode that prints the top chunks and their
**distance scores** without calling Groq.

**Command:**

```bash
./venv/Scripts/python.exe rag.py --retrieve
```

(The question it tests is hard-coded at the bottom of `rag.py`:
*"What foods are good for lowering cholesterol?"*)

**What the output looked like (abridged):**

```
Question: What foods are good for lowering cholesterol?

Top 4 chunks (lower distance = more relevant):

[1] distance=0.461  source=Human-Nutrition-2020-Edition-...pdf
    ...Soluble fiber reduces cholesterol absorption...
[2] distance=0.507  source=Human-Nutrition-1539705098.pdf
    ...limiting the consumption of saturated fats and trans fats...
[3] distance=0.599  source=Human-Nutrition-1539705098.pdf
[4] distance=0.617  source=Human-Nutrition-1539705098.pdf
```

**How to read it / why it proves retrieval works:**

- **Lower distance = closer in meaning.** The scores increase (0.461 → 0.507 →
  0.599 → 0.617), i.e. chunks are correctly ordered most-relevant first.
- The #1 chunk is literally about *soluble fiber reducing cholesterol* — exactly
  on-topic.
- The question never contained the word "fiber", yet the fiber chunk was found.
  That is **embeddings matching meaning, not keywords** — the core idea of RAG.

**Verdict:** Retrieval confirmed working. (This is the course "Validation 2"
deliverable: retriever returns relevant chunks.)

---

## 2. Verify FULL RAG answer (Step B, stage 2 — uses Groq LLM)

Now we test the complete pipeline: retrieve chunks → build context →
ask Groq to answer using only that context.

**Command:**

```bash
./venv/Scripts/python.exe rag.py
```

(With no `--retrieve` flag, `rag.py` runs `answer_with_rag()` on the same
question.)

**What the output looked like:**

```
Based on the provided context, some foods that may help lower cholesterol
levels include:
1. Soluble fiber-rich foods: oatmeal, oat bran, kidney beans, apples, pears,
   citrus fruits, barley, prunes.
2. Fatty fish: mackerel, trout, herring, sardines, tuna, salmon, halibut.
3. Nuts: walnuts, almonds, peanuts, hazelnuts, pecans, pistachios.

...this is general information and not medical advice...

📚 Sources: Human-Nutrition-1539705098.pdf, Human-Nutrition-2020-Edition-...pdf
```

**How to read it / why it proves full RAG works:**

- The answer content matches the retrieved chunks (fiber, fish, nuts) → the LLM
  answered **from your documents**, not from generic memory.
- The `📚 Sources:` line lists which PDFs were used → answers are *grounded and
  traceable*, not hallucinated.
- The medical-advice disclaimer appears → the prompt instructions were followed.

**Verdict:** Full RAG confirmed working. (This is the course "Validation 3"
deliverable: the system answers from the documents.)

---

## 3. A real bug we hit and fixed (Windows-specific)

On the first full run, the LLM answer generated successfully but the program
**crashed on the very last line** with:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4da'
```

**Cause:** Windows terminals default to the `cp1252` text encoding, which cannot
print emoji (the `📚` in the Sources line). The *answer was fine* — Python just
couldn't print the emoji character.

**Fix:** force UTF-8 output at the top of `rag.py`:

```python
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
```

After this, the full run completed cleanly. (Same fix will matter for `app.py`
later, which also prints emoji like `🥗`.)

---

## 4. Note on the noisy warnings

The runs print some harmless warnings, e.g.:

- `Loading weights: 100%|...` — the embedding model loading (first run is
  slower because it downloads ~80 MB, then it's cached).
- `Warning: You are sending unauthenticated requests to the HF Hub...` — only
  about download rate limits; safe to ignore for this project.

When capturing clean output we filtered these with `grep -v`, but they do **not**
affect correctness.

---

## Quick reference — all verification commands

```bash
# from inside the nutricoach/ folder, using the venv Python:

./venv/Scripts/python.exe inspect_db.py        # Step A: DB populated? (5378 chunks, 384-dim)
./venv/Scripts/python.exe rag.py --retrieve     # Step B stage 1: retrieval only (no API key)
./venv/Scripts/python.exe rag.py                # Step B stage 2: full RAG answer (needs GROQ_API_KEY)
```
