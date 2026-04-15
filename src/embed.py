import os
import logging
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chunking import run as get_docs

# -------------------------
# CONFIG
# -------------------------
VECTOR_STORE_DIR = "data/vectorstore"
COLLECTION_NAME = "sales_docs"
EMBED_MODEL = "all-MiniLM-L6-v2"
BATCH_SIZE = 256

# -------------------------
# LOGGING SETUP
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------------------
# EMBEDDING
# -------------------------
def load_model():
    logging.info(f"Loading embedding model: {EMBED_MODEL}")
    return SentenceTransformer(EMBED_MODEL)


def embed_documents(model, docs):
    logging.info(f"Embedding {len(docs)} documents in batches of {BATCH_SIZE}...")
    embeddings = model.encode(
        docs,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    logging.info("Embedding complete.")
    return embeddings


# -------------------------
# VECTOR STORE
# -------------------------
def get_chroma_client():
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
    return client


def store_embeddings(client, docs, embeddings):
    # Delete existing collection if present (fresh rebuild)
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        logging.info(f"Deleting existing collection '{COLLECTION_NAME}'...")
        client.delete_collection(COLLECTION_NAME)

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    ids = [f"doc_{i}" for i in range(len(docs))]
    metadatas = [{"source": "chunking_pipeline", "index": i} for i in range(len(docs))]

    # Upsert in batches to avoid memory issues on large datasets
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


# -------------------------
# PIPELINE
# -------------------------
def run():
    logging.info("Stage 3: Embeddings & Vector Store")

    docs = get_docs()
    logging.info(f"Received {len(docs)} chunked documents from Stage 2.")

    model = load_model()
    embeddings = embed_documents(model, docs)

    client = get_chroma_client()
    collection = store_embeddings(client, docs, embeddings)

    logging.info(f"Vector store saved to '{VECTOR_STORE_DIR}'.")
    return client, collection


if __name__ == "__main__":
    run()
