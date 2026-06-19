# inspect_db.py — look inside your vector database
import chromadb

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("nutrition")

# how many chunks total?
print("Total chunks stored:", collection.count())

# peek at the first few chunks (with their text + metadata)
sample = collection.peek(limit=3)
for i in range(len(sample["ids"])):
    print("\n" + "=" * 60)
    print("ID:      ", sample["ids"][i])
    print("Source:  ", sample["metadatas"][i])
    print("Text:    ", sample["documents"][i][:300], "...")
    # the vector is a long list of numbers — show just its length + first 5
    vec = sample["embeddings"][i]
    print(f"Vector:   length={len(vec)}, first 5 values={vec[:5]}")