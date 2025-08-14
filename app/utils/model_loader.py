# from config_loader import 
import os 
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal, Optional,Any
from app.utils.config_loader import load_config
from langchain_groq import ChatGroq 
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
# from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
class ConfigLoader:
    def __init__(self):
        print(f"Loading config....")
        self.config = load_config()

    def __getitem__(self,key):## This method allows you to access config values using dictionary-like syntax
        return self.config[key]
    

class ModelLoader(BaseModel):
    model_provider: Literal["groq", "gemini", "openai"] = "gemini" 
    config: Optional[ConfigLoader] = Field(default = None, exclude = True) # either the config is ConfigLoader object or None

    def model_post_init(self, __context: Any)->None:
        self.config = ConfigLoader()   # model_post_init is a Pydantic V2 hook, which runs after model creation.It assigns a ConfigLoader() instance to self.config.This ensures the configuration is loaded whenever you create a ModelLoader.

    class Config:
        arbitrary_types_allowed = True  # Allows ConfigLoader (a non-Pydantic class) to be used as a field in the model.

    def load_llm(self):
        """
        Load and return the LLM model
        """
        print("LLM loading...")
        print("Loading model from provider: ")
        if self.model_provider == "groq":
            print("Loading model from GROQ:")
            groq_api_key = os.getenv("GROQ_API_KEY")
            model_name = self.config["llm"]["groq"]["model_name"]
            llm = ChatGroq(model = model_name, api_key = groq_api_key)
        elif self.model_provider =="gemini":
            print("Loading model from gemini:")
            load_dotenv()
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            model_name = self.config["llm"]["gemini"]["model_name"]
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key= gemini_api_key
            )
        elif self.model_provider =="openai":
            load_dotenv()
            print("Loading model from openai:")
            api_key = os.getenv("OPENAI_API_KEY")
            model_name = self.config["embedding_model"]["openai"]["model_name"]
            llm = OpenAIEmbeddings(model=model_name, api_key = api_key)
        else: 
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
        return llm


    
         