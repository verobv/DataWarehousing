from fastapi import FastAPI
from pydantic import BaseModel
from rag import rag_query
from fastapi.middleware.cors import CORSMiddleware

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

@app.post("/query")
def query(q: Query):
    answer = rag_query(q.question)
    return {"answer": answer}