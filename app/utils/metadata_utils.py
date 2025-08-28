from app.schemas.metadata_schema import InsuranceMetadata, LegalMetadata, ProcurementMetadata, FinancialMetadata, HRMetadata,HealthcareMetadata
class MetadataService:
    
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
    
    @staticmethod
    def normalize_dict_to_lists( metadata: dict) -> dict:
        """
        Convert every value in a dict to a list (unless it's None).
        - None → []
        - list → as-is
        - scalar → wrap in list
        """
        normalized = {}
        for key, value in metadata.items():
            if value is None:
                normalized[key] = []
            elif isinstance(value, list):
                normalized[key] = value
            else:
                normalized[key] = [value]
        return normalized
    
    @classmethod
    def Return_document_model(result):
        """Return the appropriate metadata model class based on the document type.
            - HR/Employment
            - Insurance
            - Legal/Compliance
            - Financial/Regulatory
            - Healthcare 
        """
        if result.document_types == "Insurance":
            return InsuranceMetadata
        elif result.document_types == "Healthcare":
            return HealthcareMetadata
        elif result.document_types == "Legal/Compliance":
            return LegalMetadata
        elif result.document_types == "Financial/Regulatory":
            return FinancialMetadata
        elif result.document_types == "HR/Employment":
            return HRMetadata
        else:
            return None