import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
import ollama

# 1. Load data
df = pd.read_csv("data/processed/superstore_cleaned.csv")

# 2. Create simple text documents
docs = [
    f"Order in {row['city']} ({row['region']}): {row['category']} - {row['sales']}$ sales, {row['profit']}$ profit"
    for _, row in df.iterrows()
]

# 3. Embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(docs).tolist()

# 4. Store in ChromaDB
client = chromadb.Client()
collection = client.create_collection("sales")

def add_in_batches(collection, docs, embeddings, batch_size=1000):
    for i in range(0, len(docs), batch_size):
        batch_docs = docs[i:i + batch_size]
        batch_embeddings = embeddings[i:i + batch_size]
        batch_ids = [str(j) for j in range(i, i + len(batch_docs))]

        collection.add(
            documents=batch_docs,
            embeddings=batch_embeddings,
            ids=batch_ids
        )

add_in_batches(collection, docs, embeddings)

def rag_query(query: str) -> str:

    # 5. Query
    query_emb = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_emb,
        n_results=5
    )

    context = "\n".join(results["documents"][0])

    # 6. LLM (Ollama)
    prompt = f"""
    Answer the question using ONLY the context.

    Context:
    {context}

    Question:
    {query}
    """

    response = ollama.chat(
        model="phi3",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response["message"]["content"]

    print(answer)

    return answer