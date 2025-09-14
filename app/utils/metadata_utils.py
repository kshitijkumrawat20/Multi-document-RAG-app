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
    def cosine_similarity(vec1, vec2) -> float:
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    @staticmethod
    def keyword_sementic_check(result, data, embedding_model):
        for key in result.keys():
            print(f"Comparing key: {key}", flush=True)

            if result[key] is not None and data.get(key) is not None:
                print(f"result[{key}]: {result[key]}", flush=True)
                print(f"data[{key}]: {data[key]}", flush=True)

                if isinstance(result[key], list) and isinstance(data[key], list):
                    # Filter to only strings
                    data_list = [v for v in data[key] if isinstance(v, str)]
                    val_list = [v for v in result[key] if isinstance(v, str)]
                    data_set = set(data_list)

                    if not data_list or not val_list:
                        print(f"Skipping key '{key}' due to empty valid strings.")
                        continue

                    # Precompute embeddings for data_list
                    data_embeddings = {val: embedding_model.embed_query(val) for val in data_list}

                    # Precompute embeddings for val_list
                    val_embeddings_list = embedding_model.embed_documents(val_list)

                    for idx, val in enumerate(val_list):
                        print(f"Comparing value: {val}", flush=True)

                        if val in data_set:
                            print(f"'{val}' found in data['{key}']", flush=True)
                        else:
                            print(f"'{val}' NOT found in data['{key}']", flush=True)
                            val_vector = val_embeddings_list[idx]

                            for data_val, data_vector in data_embeddings.items():
                                similarity = MetadataService.cosine_similarity(val_vector, data_vector)
                                print(f"Cosine similarity between '{val}' and '{data_val}': {similarity}", flush=True)
                                if similarity > 0.90:
                                    print(f"'{val}' is similar to '{data_val}' with similarity {similarity}", flush=True)
                                    result[key][idx] = data_val
                                    break
                                else:
                                    print(f"'{val}' is NOT similar to '{data_val}' with similarity {similarity}", flush=True)

        return result