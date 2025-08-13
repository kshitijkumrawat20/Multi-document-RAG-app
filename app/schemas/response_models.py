from pydantic import BaseModel, model_validator,field_validator
from typing import List, Dict, Any, Optional
import json
from schemas.request_models import QuerySpec, LogicResult
class APIResponse(BaseModel):
    query_spec: QuerySpec
    logic_result: LogicResult
    debug: Optional[Dict[str, Any]] = None