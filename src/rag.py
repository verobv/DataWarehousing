import pandas as pd
from sentence_transformers import SentenceTransformer
import ollama
from embed import run as embed

# get from embed 

client, collection, docs, embeddings, model = embed()

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

    # query

    query_emb = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_emb,
        n_results=5
    )

    context = "\n".join(results["documents"][0])

    # Ollama 
    
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