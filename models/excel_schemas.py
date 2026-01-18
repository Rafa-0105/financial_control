from pydantic import BaseModel, Field, validator
from typing import List, Optional, Any, Dict
from enum import Enum

class FormulaType(str, Enum):
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    ADD = "add"
    SUBTRACT = "subtract"
    PERCENTAGE = "percentage"

class MonthEnum(str, Enum):
    JANEIRO = "janeiro"
    FEVEREIRO = "fevereiro"
    MARCO = "marco"
    ABRIL = "abril"
    MAIO = "maio"
    JUNHO = "junho"
    JULHO = "julho"
    AGOSTO = "agosto"
    SETEMBRO = "setembro"
    OUTUBRO = "outubro"
    NOVEMBRO = "novembro"
    DEZEMBRO = "dezembro"

class UpdateItem(BaseModel):
    id: int
    janeiro: Optional[float] = None
    fevereiro: Optional[float] = None
    marco: Optional[float] = None
    abril: Optional[float] = None
    maio: Optional[float] = None
    junho: Optional[float] = None
    julho: Optional[float] = None
    agosto: Optional[float] = None
    setembro: Optional[float] = None
    outubro: Optional[float] = None
    novembro: Optional[float] = None
    dezembro: Optional[float] = None

class BatchUpdateRequest(BaseModel):
    updates: List[UpdateItem]

class BatchDeleteRequest(BaseModel):
    ids: List[int]

class FormulaRequest(BaseModel):
    target_id: int
    target_month: MonthEnum
    formula: FormulaType
    value: float

class RevertRequest(BaseModel):
    field: str
    version: int

class FilterParams(BaseModel):
    min_total: Optional[float] = None
    max_total: Optional[float] = None
    month: Optional[MonthEnum] = None
    min_month_val: Optional[float] = None
    max_month_val: Optional[float] = None
    despesa_like: Optional[str] = None

class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"

class SortParams(BaseModel):
    order_by: str = "id"
    direction: SortDirection = SortDirection.ASC

class CellHistoryResponse(BaseModel):
    id: int
    despesa_id: int
    field: str
    old_value: Optional[float]
    new_value: Optional[float]
    timestamp: Any
    user_id: Optional[int]

class MonthlyAnalyticsResponse(BaseModel):
    totals: Dict[str, float]

class TopDespesasParams(BaseModel):
    limit: int = 10
