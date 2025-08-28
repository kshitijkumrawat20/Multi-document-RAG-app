import os
from dotenv import load_dotenv
from typing import Union, List

class QueryEmbedding:
    def __init__(self, query: str, embedding_model):
        self.query = query
        self.embedding_model = embedding_model

    def get_embedding(self):
        e_main = self.embedding_model.embed_query(self.query)
        return e_main
