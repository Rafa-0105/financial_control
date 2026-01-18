from fastapi import APIRouter, HTTPException
from database.connection_db import get_all_despesas, get_despesa_by_id

router = APIRouter()

@router.get('/despesas')
def read_all_despesas():
    return {"data": get_all_despesas()}

@router.get('/despesas/{despesa_id}')
def read_despesa(despesa_id: int):
    despesa = get_despesa_by_id(despesa_id)
    if not despesa:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    return {"data": despesa}
