# ingest.py — load (PDF + TXT) → chunk → embed → index into ChromaDB
import os
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

DATA_DIR = "data"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

def load_documents(folder):
    docs = []
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if filename.lower().endswith(".pdf"):
            reader = PdfReader(path)
            text = "".join((page.extract_text() or "") + "\n" for page in reader.pages)
        elif filename.lower().endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            continue  # skip anything that's not pdf or txt
        docs.append({"source": filename, "text": text})
        flag = "  ⚠️ very little text — scanned PDF?" if len(text) < 200 else ""
        print(f"Loaded {filename} ({len(text)} characters){flag}")
    return docs

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks, start = [], 0
    while start < len(text):
        chunk = text[start:start + size].strip()
        if chunk:
            chunks.append(chunk)
        start += size - overlap
    return chunks

def main():
    docs = load_documents(DATA_DIR)
    if not docs:
        print("No documents found in data/. Add your PDFs/TXT files first.")
        return

    print("\nLoading embedding model (downloads ~80MB on first run, then cached)...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    client = chromadb.PersistentClient(path="chroma_db")
    # clean reset so re-running doesn't duplicate data (works on all versions)
    try:
        client.delete_collection("nutrition")
    except Exception:
        pass
    collection = client.create_collection("nutrition")

    all_chunks, metadatas, ids, counter = [], [], [], 0
    for doc in docs:
        for chunk in chunk_text(doc["text"]):
            all_chunks.append(chunk)
            metadatas.append({"source": doc["source"]})
            ids.append(f"chunk_{counter}")
            counter += 1

    if not all_chunks:
        print("No chunks created — your files may have no extractable text.")
        return

    print(f"\nCreated {len(all_chunks)} chunks. Embedding...")
    embeddings = embedder.encode(all_chunks, show_progress_bar=True).tolist()

    collection.add(documents=all_chunks, embeddings=embeddings,
                   metadatas=metadatas, ids=ids)

    print(f"\n✅ Done. Stored {len(all_chunks)} chunks in ChromaDB (folder: chroma_db/).")
    print("\n--- First chunk preview (sanity check) ---")
    print(all_chunks[0][:400])

if __name__ == "__main__":
    main()