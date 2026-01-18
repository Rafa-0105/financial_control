from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.excel_schemas import BatchUpdateRequest, BatchDeleteRequest, UpdateItem
from models.schemas import DespesaCreate, DespesaResponseNested
from database.batch_operations import batch_update_despessas, batch_delete_despessas, batch_create_despessas

router = APIRouter(prefix="/despesas/batch", tags=["Batch Operations"])

@router.post("/update", response_model=List[DespesaResponseNested])
async def update_batch(request: BatchUpdateRequest):
    try:
        updates = [item.dict() for item in request.updates]
        return batch_update_despessas(updates)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/delete")
async def delete_batch(request: BatchDeleteRequest):
    try:
        count = batch_delete_despessas(request.ids)
        return {"message": f"Deleted {count} despesas", "deleted_count": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/create", response_model=List[DespesaResponseNested])
async def create_batch(despessas: List[DespesaCreate]):
    try:
        items = [item.dict() for item in despessas]
        return batch_create_despessas(items)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
