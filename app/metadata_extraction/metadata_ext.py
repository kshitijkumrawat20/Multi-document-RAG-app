import json
from langchain_core.exceptions import OutputParserException
from langchain_core.documents import Document
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from typing import Type
from pydantic import BaseModel
# wrap parser with fixer once
# pydantic_parser = PydanticOutputParser(pydantic_object=InsuranceMetadata)
# fixing_parser = OutputFixingParser.from_llm(llm=llm, parser=pydantic_parser) 


class MetadataExtractor:
    def __init__(self, llm = None):
        self.llm = llm

    def extractMetadata_query(self, metadata_class : Type[BaseModel],document: Document, known_keywords: dict) -> BaseModel:
        parser = PydanticOutputParser(pydantic_object=metadata_class)

        schema_str = json.dumps(metadata_class.model_json_schema(), indent=2)
        keywords_str = json.dumps(known_keywords, indent=2)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an information extraction system. 
            Extract only the required metadata from the user query using the existing known keywords. 

            ⚠️ CRITICAL FORMATTING RULES:
            - ALL fields must be arrays/lists, even if there's only one value
            - For single values, wrap in brackets: "doc_id": ["single_value"]
            - For multiple values: "coverage_type": ["value1", "value2", "value3"]
            - For null/empty fields, use: null (not empty arrays)
            
            ⚠️ Content Rules:
            - For exclusions and obligations, DO NOT copy full sentences. 
            - Instead, extract only concise normalized keywords (2–5 words max each).
            - Use existing keywords if they already exist in the provided list.
            - Prefer to reuse existing keywords if they are semantically the same.  
            - If you find a new keyword that is a sub-type or more specific variant of an existing one, keep both:  
            reuse the closest match from existing keywords, and also add the new one.  
            - In that case, set added_new_keyword=true.
            - Do not include raw paragraphs in the output.
             
            Schema you must follow:
            {schema}

            Existing Keywords:
            {keywords}
            """),
            ("human", "Text:\n{document_content}")
        ])
        chain = prompt | self.llm | parser

        try:
            result = chain.invoke({
                "schema": schema_str,
                "keywords": keywords_str,
                "document_content": document.page_content
            })
            return result
        except OutputParserException as e:
            print(f"⚠️ Parser failed on doc {document.metadata.get('source')} | error: {e}")
            return metadata_class(added_new_keyword=False)
    
    def extractMetadata(self, metadata_class : Type[BaseModel], document: Document, known_keywords: dict) -> BaseModel:
        parser = PydanticOutputParser(pydantic_object=metadata_class)

        schema_str = json.dumps(metadata_class.model_json_schema(), indent=2)
        keywords_str = json.dumps(known_keywords, indent=2)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an information extraction system. 
            Extract only the required metadata from the text according to schema given below. 

            ⚠️ CRITICAL FORMATTING RULES:
            - ALL fields must be arrays/lists, even if there's only one value
            - For single values, wrap in brackets: "doc_id": ["single_value"]
            - For multiple values: "coverage_type": ["value1", "value2", "value3"]
            - For null/empty fields, use: null (not empty arrays)
            
            ⚠️ Content Rules:
            - For exclusions and obligations, DO NOT copy full sentences. 
            - Instead, extract only concise normalized keywords (2–5 words max each).
            - Use existing keywords if they already exist in the provided list.
            - Prefer to reuse existing keywords if they are semantically the same.  
            - If you find a new keyword that is a **sub-type** or **more specific variant** of an existing one, keep both:  
            *reuse the closest match from existing keywords*, and also add the new one.  
            - In that case, set `added_new_keyword=true`.
            - Do not include raw paragraphs in the output.
            
            Schema you must follow:
            {schema}

            Existing Keywords:
            {keywords}
            """),
            ("human", "Text:\n{document_content}")
        ])
        # - Use existing keywords if they already exist in the provided list.
        #     - Only create a new keyword if absolutely necessary, and set `added_new_keyword=true`.
        #     - New keywords must be short (1–3 words).
        #     - Do NOT invent different variations (e.g., if "Medical" already exists, do not output "Mediclaim Plus").
        #     - For list fields (like exclusions), reuse existing keywords where possible.
        chain = prompt | self.llm | parser

        try:
            result = chain.invoke({
                "schema": schema_str,
                "keywords": keywords_str,
                "document_content": document.page_content
            })
            return result
        except OutputParserException as e:
            print(f"⚠️ Parser failed on doc {document.metadata.get('source')} | error: {e}")
            return metadata_class(added_new_keyword=False)   # instantiate fallback