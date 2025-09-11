from app.schemas.metadata_schema import InsuranceMetadata, CommonMetaData, HealthcareMetadata, HRMetadata, LegalMetadata,FinancialMetadata,ProcurementMetadata
from app.schemas.request_models import DocumentTypeSchema
import numpy as np
import os 
import json

class MetadataService:
    def __init__(self):
        self.metadata_models = {
            "Insurance": InsuranceMetadata,
            "HR/Employment": HRMetadata,
            "Legal/Compliance": LegalMetadata,
            "Financial/Regulatory": FinancialMetadata,
            "Government/Public Policy": CommonMetaData,
            "Technical/IT Policies": CommonMetaData,
            "Healthcare/Pharma": HealthcareMetadata,
            "Procurement/Vendor Management": ProcurementMetadata
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
    
    @staticmethod
    def cosine_similarity(text1, text2, embedding_model) -> float:
        vector1 = embedding_model.embed_query(text1)
        vector2 = embedding_model.embed_query(text2)
        cosine_similarity = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        return cosine_similarity
    
    @staticmethod
    def keyword_sementic_check(result, data, embedding_model):

        # result = result.model_dump()
        # data = json.load(open(data, 'r'))
        # Compare all keys present in both result and data, and check if any value in result[key] is present in data[key]
        for key in result.keys():
            print(f"Comparing key: {key}",flush=True)
            # Only check if both result[key] and data[key] are not None and are lists
            if result[key] is not None and data.get(key) is not None:
                print(f"result[{key}]: {result[key]}",flush=True)
                print(f"data[{key}]: {data[key]}",flush=True)
                # Ensure both are lists (skip if not)
                if isinstance(result[key], list) and isinstance(data[key], list):
                    for idx,val in enumerate(result[key]):
                        print(f"Comparing value: {val}",flush=True)
                        if val in data[key]:
                            print(f"'{val}' found in data['{key}']")
                        else:
                            print(f"'{val}' NOT found in data['{key}']")
                            for data_val in data[key]:
                                similarity = MetadataService.cosine_similarity(val, data_val,embedding_model)
                                print(f"Cosine similarity between '{val}' and '{data_val}': {similarity}")
                                if similarity > 0.90:
                                    print(f"'{val}' is similar to '{data_val}' with similarity {similarity}",flush=True)
                                    ## if similarity is greater than 0.90, then consider it as matched and replace the value in result with data value
                                    result[key][idx] = data_val
                                else:
                                    print(f"'{val}' is NOT similar to '{data_val}' with similarity {similarity}",flush=True)
        return result