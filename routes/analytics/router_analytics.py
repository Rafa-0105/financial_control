from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict
from database.batch_operations import get_monthly_analytics, get_top_expenses
from models.schemas import DespesaResponseNested

router = APIRouter(prefix="/despesas/analytics", tags=["Analytics & Reports"])

@router.get("/monthly")
async def monthly_analytics():
    try:
        return get_monthly_analytics()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/top", response_model=List[DespesaResponseNested])
async def top_expenses(limit: int = Query(10, gt=0)):
    try:
        return get_top_expenses(limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/trends")
async def analytics_trends():
    try:
        monthly = get_monthly_analytics()
        if not monthly:
            return {"highest": None, "lowest": None}
        
        sorted_months = sorted(monthly.items(), key=lambda x: x[1])
        return {
            "lowest_month": sorted_months[0][0],
            "lowest_value": sorted_months[0][1],
            "highest_month": sorted_months[-1][0],
            "highest_value": sorted_months[-1][1],
            "trend": "up" if sorted_months[-1][1] > sorted_months[0][1] else "down"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
