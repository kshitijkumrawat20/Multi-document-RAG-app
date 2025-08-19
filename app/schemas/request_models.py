from pydantic import BaseModel, model_validator,field_validator, HttpUrl, Field
from typing import List, Dict, Any, Optional, Union
import json
class QuerySpec(BaseModel):
    raw_query: str # query of the user
    intent: str # High-level purpose, e.g., "coverage_check" — helps routing aur rules.
    entities: Dict[str, Union[str, List[str]]] = Field(default_factory= dict) # Extracted items (policy number, dates, amounts) — structured
    constraints : Dict[str, Any] = Field(default_factory=dict) # filters like {"jurisdiction":"IN","incident_date":"2024-01-01"}
    answer_type: Optional[str] = "detailed" 
    followups: Optional[List[str]] = Field(default_factory=list) # followups for user

    @model_validator(mode = "before")
    @classmethod
    def parse_nested_json(cls, values): # parsing nested json to load
        for field in ['entities', 'constraints']:
            val = values.get(field)
            if isinstance(val, str):
                try:
                    values[field] = json.loads(val)
                except json.JSONDecodeError:
                    pass
        return values

class ClauseHit(BaseModel):
    doc_id : str # id of the document
    page: int # pdf page id 
    chunk_id: str  
    text: str # Evidence text used for answer.
    metadata: Dict[str, Any] = Field(default_factory=dict) # metadata
    score: float  # Retrieval similarity score
    boost: Optional[float] = None
    combined_score: Optional[float] = None

    @field_validator("metadata", mode="before")
    def parse_metadata(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v.strip() else {}
            except json.JSONDecodeError:
                return {}
        return v

class LogicResult(BaseModel):
    answer: str
    decision: str # "covered"/"not_covered"/"conditional"
    confidence: float # 0..1 score for calibration/thresholding.
    evidence: List[ClauseHit]  = Field(default_factory=list) # List of ClauseHit used to justify the answer.
    rationale: Optional[str] = None # Short human-readable reason (audit-friendly).
    
class HackRxRunRequest(BaseModel):
    documents: HttpUrl = Field(
        ...,
        description="URL to the document (PDF, DOCX, or email blob)"
    )
    questions: List[str] = Field(
        ...,
        description="List of questions to query against the document"
    )





