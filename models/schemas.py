from pydantic import BaseModel, Field
from typing import Optional

class DespesaBase(BaseModel):
    despesa: str = Field(..., min_length=1, max_length=100)
    
    janeiro: Optional[float] = Field(default=0.00, ge=0)
    fevereiro: Optional[float] = Field(default=0.00, ge=0)
    marco: Optional[float] = Field(default=0.00, ge=0)
    abril: Optional[float] = Field(default=0.00, ge=0)
    maio: Optional[float] = Field(default=0.00, ge=0)
    junho: Optional[float] = Field(default=0.00, ge=0)
    julho: Optional[float] = Field(default=0.00, ge=0)
    agosto: Optional[float] = Field(default=0.00, ge=0)
    setembro: Optional[float] = Field(default=0.00, ge=0)
    outubro: Optional[float] = Field(default=0.00, ge=0)
    novembro: Optional[float] = Field(default=0.00, ge=0)
    dezembro: Optional[float] = Field(default=0.00, ge=0)

class DespesaCreate(DespesaBase):
    pass

class DespesaUpdate(BaseModel):
    despesa: Optional[str] = Field(None, min_length=1, max_length=100)
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

class DespesaMonthlyData(BaseModel):
    janeiro: Optional[float] = 0.0
    fevereiro: Optional[float] = 0.0
    marco: Optional[float] = 0.0
    abril: Optional[float] = 0.0
    maio: Optional[float] = 0.0
    junho: Optional[float] = 0.0
    julho: Optional[float] = 0.0
    agosto: Optional[float] = 0.0
    setembro: Optional[float] = 0.0
    outubro: Optional[float] = 0.0
    novembro: Optional[float] = 0.0
    dezembro: Optional[float] = 0.0

class DespesaResponseNested(BaseModel):
    id: int
    despesa: str
    monthly_data: DespesaMonthlyData
    annual_total: float

    class Config:
        from_attributes = True
