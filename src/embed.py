import os
import logging
import json
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chunking import run as get_docs

# config

VECTOR_STORE_DIR = "data/vectorstore"
COLLECTION_NAME = "sales_docs"
EMBED_MODEL = "all-MiniLM-L6-v2"
BATCH_SIZE = 256
RESET_COLLECTION = True

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# embedding 

def load_model():
    
    logging.info(f"Loading embedding model: {EMBED_MODEL}")
    
    return SentenceTransformer(EMBED_MODEL)

def prepare_docs(docs: List[Dict]) -> Tuple[List[str], List[Dict]]:

    texts = []
    metadatas = []

    for i, doc in enumerate(docs):
        if isinstance(doc, dict):
            texts.append(doc['text'])
            metadatas.append(doc.get('metadata', {}))
        else:
            texts.append(doc)
            metadatas.append({"type": "unknown", "index": i})

    return texts, metadatas
    
def embed_documents(model, docs:List[str]):
    
    logging.info(f"Embedding {len(docs)} documents in batches of {BATCH_SIZE}...")
    
    embeddings = model.encode(
        docs,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    
    logging.info("Embedding complete.")
    
    return embeddings

# vector store 

def get_chroma_client():
    
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    
    return chromadb.PersistentClient(path=VECTOR_STORE_DIR)
    
def store_embeddings(client, docs, embeddings, metadatas):

    # delete existing collection if present (fresh rebuild)

    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        if RESET_COLLECTION:
            logging.info(f"Deleting existing collection '{COLLECTION_NAME}'...")
            client.delete_collection(COLLECTION_NAME)
        else:
            logging.info(f"Using existing collection '{COLLECTION_NAME}'")
            return client.get_collection(COLLECTION_NAME)

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    ids = [f"doc_{i}" for i in range(len(docs))]

    # upsert in batches to avoid memory issues on large datasets

    for start in range(0, len(docs), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(docs))
        collection.add(
            ids=ids[start:end],
            documents=docs[start:end],
            embeddings=embeddings[start:end].tolist(),
            metadatas=metadatas[start:end]
        )
        logging.info(f"Stored documents {start}–{end - 1}")

    logging.info(f"Total documents stored in '{COLLECTION_NAME}': {collection.count()}")
    
    return collection

# retrieval layer

def query(collection, model, question, n_results):

    query_embedding = model.encode([question]).tolist()

    analytical_keywords = [
        "highest", "lowest", "trend", "compare",
        "most", "top", "change", "over time"
    ]

    is_analytical = any(k in question.lower() for k in analytical_keywords)

    if is_analytical:
        results = collection.query(
            query_embeddings = query_embedding,
            n_results=n_results,
            where={"type": "analysis"}
        )
    else:
        results = collection.query(
            query_embeddings = query_embedding,
            n_results=n_results
        )

    return results

# pipeline

def run():

    logging.info("Starting embeddings and setting up vector store")

    if os.path.exists("data/docs.json"):
        with open("data/docs.json", "r") as f:
            docs = json.load(f)
    else:
        docs = get_docs()

        with open("data/docs.json", "w") as f:
            json.dump(docs, f)
            
    logging.info(f"Received {len(docs)} chunked documents.")

    model = load_model()
    texts, metadatas = prepare_docs(docs)

    embeddings = embed_documents(model, texts)

    client = get_chroma_client()
    collection = store_embeddings(client, texts, embeddings, metadatas)

    logging.info(f"Vector store saved to '{VECTOR_STORE_DIR}'.")
    
    return client, collection, model

if __name__ == "__main__":
    run()
