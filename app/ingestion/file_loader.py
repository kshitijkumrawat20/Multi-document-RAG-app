import requests
from langchain_community.document_loaders import PyMuPDFLoader
import os
from langchain_community.document_loaders import Docx2txtLoader
import pymupdf
class fileloader: 
    def __init__(self):
        self.pdf_document = None

    def load_documents_form_url(self, url:str):
        """
        Load documents from a given URL and return their content."""
        
        response = requests.get(url)
        response.raise_for_status()  # Ensure we got a valid response
        # check file type
        if response.headers['Content-Type'] == 'application/pdf':
            pdf_document = pymupdf.open(stream = response.content, filetype="pdf")
            return pdf_document
        else: 
            return "FILE NOT supported"
        
        
        
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
    


    
    

        
