import fitz
import os 
import docx
import email
import extract_msg
from io import BytesIO
import requests

def load_documents_form_url(url:str):
    """
    Load documents from a given URL and return their content."""
    
    response = requests.get(url)
    response.raise_for_status()  # Ensure we got a valid response
    # check file type
    if response.headers['Content-Type'] == 'application/pdf':
        pdf_doc = fitz.open(stream = response.content, filetype="pdf")
        return pdf_doc
    else: 
        return "FILE NOT supported"
    

        
