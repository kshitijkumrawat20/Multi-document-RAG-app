import os
from dotenv import load_dotenv
from pinecone import Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from datetime import datetime
from uuid import uuid4

class VectorStore:
    def __init__(self, text_chunks, embedding_model):
        self.text_chunks = text_chunks
        self.current_time = datetime.now()
        self.embedding_model = embedding_model
        self.index, self.namespace, self.retriever = self.create_vectorestore()

    def create_vectorestore(self):
        load_dotenv()
        pinecone_key = os.getenv("PINECONE_API_KEY")
        pc = Pinecone(api_key=pinecone_key)
        # pc._vector_api.api_client.pool_threads = 1  
        time_string = self.current_time.strftime("%Y-%m-%d-%H-%M")
        index_name = f"rag-project"
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
        uuids = [str(uuid4()) for _ in range(len(self.text_chunks)) ]
        vector_store = PineconeVectorStore(index = index, embedding=self.embedding_model)
        name_space = f"hackrx-index{time_string}"
        vector_store.add_documents(documents=self.text_chunks, ids = uuids,namespace = name_space )
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5},
        )

        return index, name_space, retriever


