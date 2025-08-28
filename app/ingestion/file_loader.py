import requests
from langchain_community.document_loaders import PyMuPDFLoader
import os
from langchain_community.document_loaders import Docx2txtLoader
import tempfile
from app.schemas.request_models import DocumentTypeSchema
from langchain_core.documents import Document
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

class fileloader: 
    def __init__(self):
        self.pdf_document = None

    def detect_document_type(self,llm, documents: List[Document] ) -> DocumentTypeSchema:
        """Detect the genre of document by reading first 2 page content by llm """

        document_list = [doc.page_content for doc in documents]
        document_content = " ".join(document_list)
        parser = PydanticOutputParser(pydantic_object=DocumentTypeSchema)

        # Prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a legal/HR/financial document classifier."),
            ("human", """
            You will be given the first 2 pages of a document. 
            Classify it into one of the following categories:
            - HR/Employment
            - Insurance
            - Legal/Compliance
            - Financial/Regulatory
            - Government/Public Policy
            - Technical/IT Policies

            Respond strictly in JSON that matches the schema.

            {format_instructions}

            Document content:
            {document_content}
            """),
        ])
        chain = prompt | llm | parser 

        result: DocumentTypeSchema = chain.invoke({
            "document_content": document_content,
            "format_instructions": parser.get_format_instructions()
        })
        return result
    def get_file_type_by_extension(self,filename):
        _, extension = os.path.splitext(filename)
        extension = extension.lower()
        if extension == ".txt":
            return "text"
        elif extension == ".pdf":
            return "pdf"
        elif extension in [".doc", ".docx"]:
            return "word"
        else:
            return "unknown"

    def load_documents_from_url(self, url: str):
        response = requests.get(url)
        response.raise_for_status()
        if response.headers['Content-Type'] == 'application/pdf':
            # Save PDF to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name
            
            # Load PDF from the temporary file path
            loader = PyMuPDFLoader(tmp_file_path)
            docs = loader.load()
            return docs
        else:
            raise ValueError("File type not supported, expected a PDF.")
              
    def load_pdf(self, path:str):
        """ Load PDF from a local path and return its content."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"The file {path} does not exist.")
        loader = PyMuPDFLoader(path)
        pdf_document = loader.load()
        return pdf_document
    
    ## word document processing

    def load_word_document(self, path: str) :
        try: 
            docx_loader = Docx2txtLoader(path)
            docs = docx_loader.load()
            return docs
        except Exception as e:
            print(e)
    


    
    

        
