from fastapi import FastAPI
from pydantic import BaseModel
from rag import rag_query
from fastapi.middleware.cors import CORSMiddleware

# minimun API so that the frontend works 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str

@app.get("/")
def root():
    return {"message": "API is running"}

# sends queries to RAG and sends answers to frontend

@app.post("/query")
def query(q: Query):
    answer = rag_query(q.question)
    return {"answer": answer}