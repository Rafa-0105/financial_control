from fastapi import APIRouter, HTTPException
from database.connection_db import delete_despesa

router = APIRouter()

@router.delete('/despesas/{despesa_id}', status_code=200)
def delete_despesa_endpoint(despesa_id: int):
    if not delete_despesa(despesa_id):
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    return None
