from fastapi import APIRouter, HTTPException
from database.connection_db import update_despesa
from models.schemas import DespesaUpdate, DespesaResponseNested

router = APIRouter()

@router.put('/despesas/{despesa_id}', response_model=DespesaResponseNested)
def update_despesa_endpoint(despesa_id: int, despesa: DespesaUpdate):
    print("Passou por aqui")
    despesa_dict = despesa.model_dump(exclude_unset=True)
    result = update_despesa(despesa_id, despesa_dict)
    
    if not result:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    return result
