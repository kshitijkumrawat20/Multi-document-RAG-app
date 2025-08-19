from pydantic import BaseModel, model_validator,field_validator, HttpUrl, Field
from typing import List, Dict, Any, Optional, Union
import json
class QuerySpec(BaseModel):
    raw_query: str # query of the user
    intent: str # High-level purpose, e.g., "coverage_check" — helps routing aur rules.
    entities: Dict[str, Union[str, List[str]]] = Field(default_factory= dict)
    constraints : Dict[str, Any] = Field(default_factory=dict)
    answer_type: Optional[str] = "detailed" 
    followups: Optional[List[str]] = Field(default_factory=list)

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
    doc_id : str
    page: int
    chunk_id: str 
    text: str 
    metadata: Dict[str, Any] = Field(default_factory=dict)
    score: float 
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
    confidence: float
    evidence: List[ClauseHit]  = Field(default_factory=list)
    rationale: Optional[str] = None
    
class HackRxRunRequest(BaseModel):
    documents: HttpUrl = Field(
        ...,
        description="URL to the document (PDF, DOCX, or email blob)"
    )
    questions: List[str] = Field(
        ...,
        description="List of questions to query against the document"
    )





