from pydantic import BaseModel, model_validator,field_validator
from typing import List, Dict, Any, Optional
import json
from app.schemas.request_models import QuerySpec, LogicResult
class APIResponse(BaseModel):
    answer : List