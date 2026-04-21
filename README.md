# Sales Analytics RAG Pipeline

This project implements a **Retrieval-Augmented Generation (RAG)** pipeline on top of a sales dataset.
It combines **data engineering (ETL)** with **LLM-powered querying**, allowing natural language questions over structured business data.

---

## Project Overview

The pipeline consists of:

1. **ETL Pipeline**

   * Download dataset from Kaggle
   * Clean and preprocess data
   * Store structured dataset

2. **Document Generation**

   * Convert rows into natural language
   * Generate aggregated summaries:

     * Monthly trends
     * Category performance
     * Regional performance

3. **Embeddings & Vector Store**

   * Transform text into embeddings
   * Store in a vector database

4. **RAG System**

   * Retrieve relevant documents
   * Generate answers using an LLM

---

## Example Queries

* “Which region has the highest sales?”
* “What is the most profitable category?”
* “How did sales evolve over time?”

---

## Project Structure

```
project/
│
├── data/
│   ├── raw/                # Raw downloaded data
│   ├── processed/          # Cleaned dataset
│
├── src/
│   ├── etl_pipeline.py     # ETL pipeline
│   ├── generate_docs.py    # Convert data → text
│   ├── embed.py            # Create embeddings
│   ├── rag.py              # RAG query pipeline
│
├── requirements.txt
├── README.md
```

---

## Installation

### 1. Clone the repository

```
git clone  https://github.com/verobv/DataWarehousing.git
cd DataWarehousing
```

---

### 2. Create environment (recommended)

Using Conda:

```
conda create -n rag-project python=3.10
conda activate rag-project
```

Or using venv:

```
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Mac/Linux
```

---

### 3. Install dependencies

```
pip install -r requirements.txt
```

Or manually:

```
pip install pandas numpy sentence-transformers chromadb requests kaggle ollama fastapi pydantic
```

---

### 4. Kaggle API setup

1. Go to your Kaggle account
2. Download `kaggle.json`
3. Place it in:

Windows:

```
C:\Users\<your-user>\.kaggle\kaggle.json
```

Mac/Linux:

```
~/.kaggle/kaggle.json
```

---

### 5. Install Ollama (for LLM)

Download and install from: https://ollama.com

Then pull a model:

```
ollama pull phi3
```

Run it:

```
ollama run phi3
```

---

## Running the Application

### Step 1 — In a different terminal from the ollama above, run

```
uvicorn main:app --reload
```

---

### Step 2 — In a different terminal, run the frontend

```
npm run dev
```

---

### Step 3 — Open the frontend

```
http://localhost:5173/
```

---

### Step 4 — Click on one of the queries and wait for the LLM's answer!

```
You will also see it printed on the backend terminal
```

---

## 🔧 Key Features

* Clean ETL pipeline with logging
* Robust CSV loading (handles encoding issues)
* Aggregated summaries for better retrieval
* Local LLM via Ollama (no API costs)
* Vector search using ChromaDB

---

## Architecture

```
        ┌──────────────┐
        │   Kaggle     │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │     ETL      │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Text Docs    │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Embeddings   │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Vector DB    │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │     LLM      │
        └──────────────┘
```

## Notes

* Use `python`, not `python3` on Windows (Anaconda environments)
* If CSV fails to load, ensure encoding is set to `latin-1`
* Make sure Ollama is running before querying

---

## Authors

Verónica — Data Analyst transitioning into Software Engineering
Focus: Data Engineering, Backend Systems, and Applied AI

Prerna - 

---
