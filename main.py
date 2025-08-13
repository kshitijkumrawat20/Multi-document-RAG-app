from app.utils.model_loader import ModelLoader
from app.ingestion.file_loader import load_documents_form_url
from app.ingestion.text_splitter import text_splitting
from app.reseasoning.query_parser import parsing_query
from app.reseasoning.descision_maker import evaluate_with_llm
from app.retrieval.retriever import retrieval_from_pinecone_vectoreStore
from app.schemas.request_models import QuerySpec,LogicResult, ClauseHit, HackRxRunRequest
from app.schemas.response_models import APIResponse
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from app.embedding.embeder import get_query_embedding
from app.embedding.vectore_store import create_vectore_store
app = FastAPI(title="RAG app")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def verify_bearer_token(authorization: Optional[str] = Header(None)):
    expected_token = "Bearer cc13b8bb7f4bc1570c8a39bda8c9d4c34b2be6b8abe1044c89abf49b28cee3f8"
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split("Bearer ")[1]
    if token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid token")
    return True

@app.post("/api/v1/hackrx/run", response_model=APIResponse)
async def run_hackrx(request: HackRxRunRequest , authorized: bool = Depends(verify_bearer_token)):
    ## model initialisation 
    # LLM
    model_loader = ModelLoader(model_loader= "gemini")
    llm = model_loader.load_llm()

    # Embedding model 
    model_loader = ModelLoader(model_provider="openai")
    embedding_model = model_loader.load_llm()
    answers = []
    for question in request.questions:
        
        #1. parsing query 
        parsed_query = parsing_query(query=question, llm = llm)

        #2 emebed the query
        embedding = get_query_embedding(query_spec = parsed_query, embedding_model=embedding_model)
        # 3.
        # # Step 2 — Retrieve
        top_hits = retrieval_from_pinecone_vectoreStore(, embedding, top_k=3)
        






    

