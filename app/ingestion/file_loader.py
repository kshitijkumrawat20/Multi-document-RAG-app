import requests
from langchain_community.document_loaders import PyMuPDFLoader
import os
from langchain_community.document_loaders import Docx2txtLoader
import pymupdf
import tempfile

class fileloader: 
    def __init__(self):
        self.pdf_document = None
    
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
    


    
    

        
