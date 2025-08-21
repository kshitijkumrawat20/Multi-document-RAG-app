## creating chunks
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from uuid import uuid4
from typing import List, Dict

class splitting_text:

    def _clean_text(self, text:str)-> str: 
        """Clean extracted page content"""
        # remove excessive whitespace 
        text = " ".join(text.split())
        return text

    def text_splitting(self, doc_content: str) -> List[Document]:
        """
        split the documents into chunks and add metadata fields with every document
        """
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        all_chunks = []

        for i, page in enumerate(doc_content): 
            # reset per page
            try:
                text = page.get_text()
            except:
                text = page.page_content
                
            text = self._clean_text(text)

            if text.strip():
                uuid = str(uuid4())
                temp_doc = Document(
                    page_content=text,
                    metadata={
                        **page.metadata,
                        "page_no": i,
                        "doc_id": uuid,
                        "chunk_id": f"{uuid}_p{i}",
                        "type": "text"
                    }
                )
                chunks = splitter.split_documents([temp_doc])
                all_chunks.extend(chunks)

        return all_chunks

