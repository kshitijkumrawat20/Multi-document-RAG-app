import requests
from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader
import os
import tempfile
from app.schemas.request_models import DocumentTypeSchema
from langchain_core.documents import Document
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.schemas.metadata_schema import InsuranceMetadata, HRMetadata, LegalMetadata, FinancialMetadata, DocumentTypeSchema

class FileLoader:
    def __init__(self, llm=None):
        self.llm = llm

    def detect_document_type(self, documents: List[Document]) -> DocumentTypeSchema:
        """Detect the genre of document by reading first 2 page content by llm."""
        
        document_content = " ".join([doc.page_content for doc in documents])
        parser = PydanticOutputParser(pydantic_object=DocumentTypeSchema)
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
            - Healthcare 

            Respond strictly in JSON that matches the schema.

            {format_instructions}

            Document content:
            {document_content}
            """),
        ])
        chain = prompt | self.llm | parser
        result: DocumentTypeSchema = chain.invoke({
            "document_content": document_content,
            "format_instructions": parser.get_format_instructions()
        })
        return result

    def load_documents_from_url(self, url: str) -> List[Document]:
        response = requests.get(url)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '')
        if content_type == 'application/pdf':
            tmp_file_path = self._save_temp_file(response.content, ".pdf")
            return self.load_pdf(tmp_file_path)
        else:
            raise ValueError("File type not supported, expected a PDF.")

    def load_pdf(self, path: str) -> List[Document]:
        """Load PDF from a local path and return its content."""
        self._validate_file_exists(path)
        loader = PyMuPDFLoader(path)
        return loader.load()

    def load_word_document(self, path: str) -> List[Document]:
        """Load Word document from a local path and return its content."""
        self._validate_file_exists(path)
        try:
            docx_loader = Docx2txtLoader(path)
            return docx_loader.load()
        except Exception as e:
            print(e)
            return []

    def _save_temp_file(self, content: bytes, suffix: str) -> str:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
            tmp_file.write(content)
            return tmp_file.name

    def _validate_file_exists(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"The file {path} does not exist.")
