from app.schemas.metadata_schema import InsuranceMetadata, CommonMetaData
from app.schemas.request_models import DocumentTypeSchema
class MetadataService:
    def __init__(self):
        self.metadata_models = {
            "Insurance": InsuranceMetadata,
            "HR/Employment": CommonMetaData,
            "Legal/Compliance": CommonMetaData,
            "Financial/Regulatory": CommonMetaData,
            "Government/Public Policy": CommonMetaData,
            "Technical/IT Policies": CommonMetaData
        }
    @staticmethod
    def format_metadata_for_pinecone(metadata: dict) -> dict:
        """
        Convert list fields in metadata to Pinecone's valid filter format using $in.
        """
        formatted = {}
        for key, value in metadata.items():
            if isinstance(value, list):
                if len(value) > 0:
                    formatted[key] = {"$in": value}
            else:
                formatted[key] = value
        return formatted

    def Return_document_model(self, doc_type_schema: DocumentTypeSchema):
        """
        Returns appropriate metadata model based on document type
        
        Args:
            doc_type_schema: DocumentTypeSchema object containing document type
        
        Returns:
            Appropriate Pydantic model class for the document type
        """
        doc_type = doc_type_schema.document_types
        return self.metadata_models.get(doc_type, CommonMetaData)
    
    @staticmethod
    def normalize_dict_to_lists(metadata: dict) -> dict:
        """Convert dict values to lists if they aren't already"""
        normalized = {}
        for key, value in metadata.items():
            if value is None:
                normalized[key] = []
            elif isinstance(value, list):
                normalized[key] = value
            else:
                normalized[key] = [value]
        return normalized