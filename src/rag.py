import ollama
from embed import run as embed
from embed import query as get_results

# get from embed 

client, collection, model = embed()

def rag_query(query: str) -> str:

    # query

    results = get_results(collection, model, query, 5)

    retrived_docs = results['documents'][0]

    context = "\n".join(retrived_docs)

    # Ollama 
    
    prompt = f"""
    You are a data analyst assistant.

    RULES:
    - Do NOT infer or guess missing information
    - Use ONLY the provided context to answer the question
    - If ranking is shown, return it exactly as listed
    - Do not mix regions and cities
    - If the answer is not explicitly in the context, say "I don't have enough information."

    Be precise and analytical.

    Context:
    {context}

    Question:
    {query}

    Answer:
    """

    response = ollama.chat(
        model="phi3",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response["message"]["content"]

    print(answer)

    return answer