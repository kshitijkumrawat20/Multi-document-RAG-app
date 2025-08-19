import pymupdf 
import os 
import requests
import pymupdf

def load_documents_form_url(url:str):
    """
    Load documents from a given URL and return their content."""
    
    response = requests.get(url)
    response.raise_for_status()  # Ensure we got a valid response
    # check file type
    if response.headers['Content-Type'] == 'application/pdf':
        pdf_doc = pymupdf.open(stream = response.content, filetype="pdf")
        return pdf_doc
    else: 
        return "FILE NOT supported"
    
def load_from_pdf(pdf_path: str):
    """Load the uploaded pdf"""
    try:
        

    
    

        
