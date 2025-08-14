import os
from dotenv import load_dotenv
from app.schemas.request_models import QuerySpec
from typing import Union, List


def get_query_embedding(query_spec: QuerySpec, embedding_model):
    # load_dotenv()
    # model_loader = ModelLoader(model_provider="openai")
    # embedding_client = model_loader.load_llm()
    q = query_spec.raw_query
    e_main =  embedding_model.embed_query(q)
    expansions = []
    if "procedure" in query_spec.entities:
        procedure_value = query_spec.entities['procedure']
        # Handle both string and list values
        if isinstance(procedure_value, list):
            procedure_str = ", ".join(procedure_value)
        else:
            procedure_str = procedure_value
        expansions.append(f"{q} OR {procedure_str} procedures related")
    return e_main,expansions
