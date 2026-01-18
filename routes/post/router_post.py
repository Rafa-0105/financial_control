from fastapi import APIRouter, HTTPException
from database.connection_db import create_despesa
from models.schemas import DespesaCreate, DespesaResponseNested

router = APIRouter()

@router.post('/despesas', response_model=DespesaResponseNested, status_code=201)
def create_new_despesa(despesa: DespesaCreate):
    despesa_dict = despesa.model_dump()
    result = create_despesa(despesa_dict)
    return result
