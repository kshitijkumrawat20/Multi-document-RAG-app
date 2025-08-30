from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    ""