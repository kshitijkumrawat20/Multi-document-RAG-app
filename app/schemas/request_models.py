from pydantic import BaseModel, model_validator,field_validator, HttpUrl, Field
from typing import List, Dict, Any, Optional, Union, Literal
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

class DocumentTypeSchema(BaseModel):
    document_types: Literal[
        "HR/Employment",
        "Insurance",
        "Legal/Compliance",
        "Financial/Regulatory",
        "Government/Public Policy",
        "Technical/IT Policies"
    ] = Field(..., description="The category/type of the document")


class CommonMetaData(BaseModel):
    # --- Common metadata (across all domains) ---
    doc_id: Optional[str] = Field(None, description="Unique document identifier")
    doc_category: Optional[List[str]] = Field(None, description="General pool/category e.g. Insurance, HR, Legal")
    doc_type: Optional[List[str]] = Field(None, description="Specific type e.g. Policy doc, Contract, Handbook")
    jurisdiction: Optional[List[str]] = Field(
    default=None, description="Applicable jurisdictions/regions/countries"
    )
    effective_date: Optional[List[str]] = Field(None, description="Date from which the document is effective")
    expiry_date: Optional[List[str]] = Field(None, description="Date until which the document is valid")
    parties: Optional[List[str]] = Field(None, description="Involved parties (e.g., employer/employee, insurer/insured)")
    obligations: Optional[List[str]] = Field(
        default=None,
        description="List of short, normalized obligation keywords (2–5 words each, no full sentences)"
    )
    penalties: Optional[List[str]] = Field(None, description="Penalties/non-compliance consequences")
    notes: Optional[List[str]] = Field(None, description="Freeform additional metadata")

class InsuranceMetadata(CommonMetaData):

    # --- Insurance ---
    policy_number: Optional[List[str]] = None
    coverage_type: Optional[List[str]] = Field(
    default=None,
    description="Type(s) of coverage. Short keywords (1–3 words each)."
    )
    premium_amount: Optional[List[str]] = None
    exclusions: Optional[List[str]] = Field(
        description="List of normalized keywords representing exclusions (short, 2-5 words each, not full paragraphs).", default=None
    )
    added_new_keyword: bool = False
    # # --- HR / Employment ---
    # policy_type: Optional[str] = None
    # applicable_roles: Optional[List[str]] = None
    # notice_period: Optional[str] = None

    # # --- Legal / Compliance ---
    # clause_type: Optional[str] = None
    # governing_law: Optional[str] = None
    # duration: Optional[str] = None

    # # --- Financial / Regulatory ---
    # section: Optional[str] = None
    # compliance_requirement: Optional[str] = None
    # reporting_frequency: Optional[str] = None

    # # --- Healthcare / Pharma ---
    # disease: Optional[str] = None
    # treatment_limit: Optional[str] = None
    # validity_period: Optional[str] = None

    # # --- Procurement / Vendor Management ---
    # vendor_name: Optional[str] = None
    # contract_value: Optional[str] = None
    # payment_terms: Optional[str] = None
    # sla_metrics: Optional[List[str]] = None

    # # --- Government / Public Policy ---
    # act_name: Optional[str] = None

    # # --- Technical / IT Policies ---
    # security_level: Optional[str] = None
    # compliance_standard: Optional[str] = None  # ISO, NIST, SOC2 etc.





