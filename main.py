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
from app.ingestion.file_loader import load_documents_form_url
from app.ingestion.text_splitter import text_splitting

app = FastAPI(title="RAG app")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def verify_bearer_token(authorization: Optional[str] = Header(None)):
    expected_token = "cc13b8bb7f4bc1570c8a39bda8c9d4c34b2be6b8abe1044c89abf49b28cee3f8"
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split("Bearer ")[1]
    if token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid token")
    return True

@app.post("/api/v1/hackrx/run", response_model=APIResponse)
async def run_hackrx(request: HackRxRunRequest ): #, authorized: bool = Depends(verify_bearer_token)
    ## model initialisation 
    # LLM
    model_loader = ModelLoader(model_loader= "gemini")
    llm = model_loader.load_llm()

    # Embedding model 
    model_loader = ModelLoader(model_provider="openai")
    embedding_model = model_loader.load_llm()
    print("LLMs are loaded!!")

    answers = []
    
    # file loading 
    document_url = request.documents
    pdf_doc = load_documents_form_url(document_url)
    print("file has been loaded")

    ## splitting into chunks 
    chunks = text_splitting(doc_content=pdf_doc)
    print("Chunks have been splitted")

    ## creating a vectore store 
    index, namespace = create_vectore_store(text_chunks=chunks, embedding_model=embedding_model)
    print("Index is created")
    for question in request.questions:
        
        #1. parsing query 
        parsed_query = parsing_query(query=question, llm = llm)
        print("Query Parsed")

        #2 emebed the query
        query_embedding, expansions = get_query_embedding(query_spec = parsed_query, embedding_model=embedding_model)
        print("Query Embedded")
        # 3.Retrieve
        top_hits = retrieval_from_pinecone_vectoreStore(pinecone_index=index, embeddings = query_embedding , top_k=3,namespace=namespace)
        print("Documents retrieved!")
        # 4. evaluate with llm 
        result = evaluate_with_llm(raw_query=question, top_clauses=top_hits, llm = llm)
        print("Answer created!")
        answers.append(result.answer)

    print("Answers are appended!")
    print(answers)
    # index.delete(delete_all=True,namespace=namespace)
    # print("index is deleted!!")
    return APIResponse(answers=answers)


        




