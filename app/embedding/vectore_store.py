import os
from dotenv import load_dotenv
from pinecone import Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from datetime import datetime
from uuid import uuid4

current_time = datetime.now()

def create_vectore_store(text_chunks:list, embedding_model):
    load_dotenv()
    pinecone_key = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=pinecone_key)
    # pc._vector_api.api_client.pool_threads = 1  
    time_string = current_time.strftime("%Y-%m-%d-%H-%M")
    index_name = f"hackrx-index"
    if not pc.has_index(index_name):
        pc.create_index(
            name = index_name,
            dimension=1536,
            metric="cosine",
            spec = ServerlessSpec(cloud="aws", region="us-east-1")
        )

    index = pc.Index(index_name)
    # model_loader = ModelLoader(model_provider="openai")
    # embedding_model = model_loader.load_llm()
    uuids = [str(uuid4()) for _ in range(len(text_chunks)) ]
    vector_store = PineconeVectorStore(index = index, embedding=embedding_model)
    name_space = f"hackrx-index{time_string}"
    vector_store.add_documents(documents=text_chunks, ids = uuids,namespace = name_space )

    return index, name_space


