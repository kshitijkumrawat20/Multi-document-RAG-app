import os
from dotenv import load_dotenv
from app.schemas.request_models import QuerySpec


def get_query_embedding(query_spec: QuerySpec, embedding_model):
    # load_dotenv()
    # model_loader = ModelLoader(model_provider="openai")
    # embedding_client = model_loader.load_llm()
    q = query_spec.raw_query
    e_main =  embedding_model.embed_query(q)
    expansions = []
    if "procedure" in query_spec.entities:
        expansions.append(f"{q} OR {query_spec.entities['procedure']} procedures related")
    return e_main, expansions
