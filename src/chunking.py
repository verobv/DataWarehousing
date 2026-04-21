import pandas as pd
import json
from etl_pipeline import run_pipeline as get_df 

# row-level documents

def create_row_docs(df):
    return df.apply(lambda row: (
        f"Order from {row['order_date'].date()} in {row['region']} region. "
        f"Category: {row['category']}, Sales: ${row['sales']:.2f}, Profit: ${row['profit']:.2f}."
    ), axis=1).tolist()

# aggregations

def create_monthly_docs(df):

    monthly = df.groupby(["year", "month"]).agg({
        "sales": "sum",
        "profit": "sum"
    }).reset_index()

    return monthly.apply(lambda row: (
        f"In {int(row['year'])}-{int(row['month']):02d}, sales were ${row['sales']:.2f} "
        f"and profit was ${row['profit']:.2f}."
    ), axis=1).tolist()

# chunking (hybrid) - small docs are unchanged while large docs are split

def chunk_text(text, size=300, overlap=50):
    chunks = []
    for i in range(0, len(text), size - overlap):
        chunks.append(text[i:i + size])
    return chunks

def apply_chunking(docs):
    chunked = []
    for doc in docs:
        if len(doc) < 300:
            chunked.append(doc)
        else:
            chunked.extend(chunk_text(doc))
    return chunked

# pipeline

def run():
    df = get_df()

    row_docs = create_row_docs(df)
    monthly_docs = create_monthly_docs(df)

    all_docs = row_docs + monthly_docs

    chunked_docs = apply_chunking(all_docs)

    with open("data/docs.json", "w") as f:
        json.dump(chunked_docs, f)

    return chunked_docs

if __name__ == "__main__":
    docs = run()
    print(f"Generated {len(docs)} documents")