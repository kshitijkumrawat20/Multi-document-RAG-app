from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from uuid import uuid4


def text_splitting(doc_content: str):
    """
    split the documents into chunks and add metadata fields with every document
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    for i,page in enumerate(doc_content): 
        text += page.get_text()
        uuid = str(uuid4())
        if text.strip():
            temp_doc = Document(page_content = text, metadata={
                "doc_id": uuid,
                "page":i,
                "chunk_id": f"{uuid}_p{i}",
                "type":"text"
                })
            text_chunks = splitter.split_documents([temp_doc])

    return text_chunks

