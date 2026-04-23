import pandas as pd
import json
from etl_pipeline import run_pipeline as get_df 
import tiktoken

CHUNKS = 200
OVERLAP = 40
enc = tiktoken.get_encoding("cl100k_base")

def load_data(path): 
    return pd.read_csv(path, parse_dates=["order_date", "ship_date"])

def count_tokens(text):
    return len(enc.encode(text))

# row-level documents

def create_row_docs(df):

    docs = []

    for _, row in df.iterrows():
        docs.append({
            "text": (
                f"Order from {row['order_date'].date()} in {row['region']} region. "
                f"Category: {row['category']}, Sales: ${row['sales']:.2f}, Profit: ${row['profit']:.2f}."
            ),
            "metadata": {
                "type": "row",
                "region": str(row["region"]).lower(),
                "category": str(row["category"]).lower(),
                "year": int(row["year"]),
                "month": int(row["month"])
            }
        })

    return docs 

# aggregations

def create_monthly_docs(df):

    df_copy = df.copy()

    docs = []

    monthly_sales = (
        df_copy.groupby("month")["sales"]
         .mean()
         .sort_values(ascending=False)
    )

    docs.append({
        "text": f"Average monthly sales ranking (seasonality): {monthly_sales.to_dict()}",
        "metadata": {
            "type": "analysis",
            "metric": "seasonality"
        }
    })

    monthly = df_copy.groupby(["year", "month"]).agg({
        "sales": "sum",
        "profit": "sum"
    }).reset_index()

    for _, row in monthly.iterrows():
        docs.append({
            "text": (
                f"In {int(row['year'])}-{int(row['month']):02d}, sales were ${row['sales']:.2f} "
                f"and profit was ${row['profit']:.2f}."
            ),
            "metadata": {
                "type": "time",
                "year": int(row["year"]),
                "month": int(row["month"])
            }
        })

    return docs

def create_analytic_docs(df):

    df_copy = df.copy()

    docs = []

    region_sales = (df_copy.groupby("region")["sales"]
                    .sum()
                    .sort_values(ascending=False)
    )

    docs.append({
        "text": (
            f"The region with the highest sales is {region_sales.idxmax()} "
            f"with ${region_sales.max():.2f}. Full ranking: {region_sales.to_dict()}."
        ),
        "metadata": {
            "type": "analysis",
            "metric": "region_sales"
        }
    })

    region_profit = (df_copy.groupby("region")["profit"]
                    .sum()
    )

    docs.append({
        "text": f"Profit by region: {region_profit.to_dict()}",
        "metadata": {
            "type": "analysis",
            "metric": "region_profit"
        }
    })

    cat_sales = (df_copy.groupby("category")["sales"]
                    .sum()
                    .sort_values(ascending=False)
    )

    docs.append({
        "text": f"Category sales ranking: {cat_sales.to_dict()}",
        "metadata": {
            "type": "analysis",
            "metric": "category_sales"
        }
    })

    city_sales = (df_copy.groupby("city")["sales"]
                    .sum()
                    .sort_values(ascending=False)
                    .head(10)
    )

    docs.append({
        "text": f"Top 10 cities by sales: {city_sales.to_dict()}",
        "metadata": {
            "type": "analysis",
            "metric": "city_sales"
        }
    })

    margin_trend = (
        df_copy.groupby(["year", "month"])["profit_margin"]
        .mean()
        .reset_index()
    )

    docs.append({
        "text": f"Profit margin trend over time: {margin_trend.to_dict(orient='records')}",
        "metadata": {
            "type": "analysis",
            "metric": "profit_trend"
        }
    })

    discounts = df_copy[df_copy['discount'] > 0]

    top_discounted_products = (
        discounts["product_name"]
         .value_counts()
         .head(10)

    )

    docs.append({
        "text": f"Top 10 discounted products: {top_discounted_products.to_dict()}",
        "metadata": {
            "type": "analysis",
            "metric": "discounted_products"
        }
    })

    subcat_margin = (
        df_copy.groupby("sub-category")
        .apply(lambda x: x['profit'].sum() / x["sales"].sum())
        .sort_values(ascending=False)
    )

    docs.append({
        "text": f"Sub-category profit margins ranking: {subcat_margin.to_dict()}",
        "metadata": {
            "type": "analysis",
            "metric": "subcat_margin"
        }
    })

    tech_furni = (
        df_copy[df_copy['category'].isin(["Technology", "Furniture"])]
        .groupby(["year", "category"])["sales"]
        .sum()
        .reset_index()
    )

    docs.append({
        "text": f"Technology vs furniture sales over time: {tech_furni.to_dict(orient='records')}",
        "metadata": {
            "type": "analysis",
            "metric": "tech_vs_furniture"
        }
    })

    return docs

# chunking (hybrid) - small docs are unchanged while large docs are split

def chunk_text(text, size=CHUNKS, overlap=OVERLAP):

    tokens = enc.encode(text)
    chunks = []

    for i in range(0, len(tokens), size - overlap):
        chunk_tokens = tokens[i:i + size]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)

    return chunks

def apply_chunking(docs):

    chunked = []

    for doc in docs:

        text = doc['text']
        tokens = enc.encode(text)

        if len(tokens) <= CHUNKS:
            chunked.append(doc)
        else:
            for chunk in chunk_text(text):
                chunked.append({
                    "text": chunk,
                    "metadata": doc['metadata']
                })

    return chunked

# pipeline  

def run():

    df = get_df()

    if df is None:
        df = load_data("data/processed/superstore_cleaned.csv")

    row_docs = create_row_docs(df)
    monthly_docs = create_monthly_docs(df)
    analytics = create_analytic_docs(df)

    all_docs = row_docs + monthly_docs + analytics

    chunked_docs = apply_chunking(all_docs)

    total_tokens = sum(len(enc.encode(doc['text'])) for doc in chunked_docs)
    print(f"Total tokens: {total_tokens}")

    with open("data/docs.json", "w") as f:
        json.dump(chunked_docs, f)

    return chunked_docs

if __name__ == "__main__":
    docs = run()
    print(f"Generated {len(docs)} documents")