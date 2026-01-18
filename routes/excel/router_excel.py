import csv
import io
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List, Optional
from models.excel_schemas import FormulaRequest, MonthEnum, FilterParams, SortDirection, RevertRequest
from models.schemas import DespesaResponseNested, DespesaCreate
from database.batch_operations import (
    calculate_column_sum, calculate_column_average, apply_excel_formula,
    get_despesa_history, revert_cell_value, filter_expenses, sort_expenses,
    batch_create_despessas, check_consistency, detect_anomalies, find_duplicates
)
from database.connection_db import get_all_despesas

router = APIRouter(prefix="/despesas", tags=["Excel-like Features"])

# 1. Calculations
@router.get("/calculate/sum")
async def get_sum(column: str = Query(..., description="Column to sum (e.g. janeiro, total)")):
    try:
        total = calculate_column_sum(column)
        return {"column": column, "sum": total}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/calculate/average")
async def get_average(column: str = Query(..., description="Column to average")):
    try:
        avg = calculate_column_average(column)
        return {"column": column, "average": avg}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/formulas/apply", response_model=DespesaResponseNested)
async def apply_formula(request: FormulaRequest):
    try:
        return apply_excel_formula(request.target_id, request.target_month.value, request.formula.value, request.value)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 2. Import/Export
@router.post("/import/csv")
async def import_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        content = await file.read()
        stream = io.StringIO(content.decode('utf-8'))
        reader = csv.DictReader(stream)
        
        to_import = []
        errors = []
        for i, row in enumerate(reader):
            try:
                # Mapping CSV headers to schema keys
                # Expected format: Despesa,Jan,Fev,Mar,Abr,Mai,Jun,Jul,Ago,Set,Out,Nov,Dez
                # We normalize to the model keys
                mapping = {
                    'Despesa': 'despesa', 'Jan': 'janeiro', 'Fev': 'fevereiro', 'Mar': 'marco',
                    'Abr': 'abril', 'Mai': 'maio', 'Jun': 'junho', 'Jul': 'julho',
                    'Ago': 'agosto', 'Set': 'setembro', 'Out': 'outubro', 'Nov': 'novembro', 'Dez': 'dezembro'
                }
                
                mapped_row = {}
                for csv_key, model_key in mapping.items():
                    val = row.get(csv_key)
                    if model_key == 'despesa':
                        mapped_row[model_key] = val
                    else:
                        mapped_row[model_key] = float(val.replace(',', '.')) if val else 0.0
                
                to_import.append(mapped_row)
            except Exception as row_error:
                errors.append(f"Row {i+1}: {str(row_error)}")
        
        if to_import:
            batch_create_despessas(to_import)
            
        return {
            "status": "success",
            "imported_count": len(to_import),
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/export/csv")
async def export_csv():
    try:
        data = get_all_despesas() # This returns formatted nested data
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        headers = ['id', 'despesa', 'janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho', 
                   'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro', 'total_anual']
        writer.writerow(headers)
        
        for item in data:
            row = [
                item['id'],
                item['despesa'],
                item['monthly_data']['janeiro'],
                item['monthly_data']['fevereiro'],
                item['monthly_data']['marco'],
                item['monthly_data']['abril'],
                item['monthly_data']['maio'],
                item['monthly_data']['junho'],
                item['monthly_data']['julho'],
                item['monthly_data']['agosto'],
                item['monthly_data']['setembro'],
                item['monthly_data']['outubro'],
                item['monthly_data']['novembro'],
                item['monthly_data']['dezembro'],
                item['annual_total']
            ]
            writer.writerow(row)
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=despesas_export.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/import/json")
async def import_json(despessas: List[DespesaCreate]):
    try:
        items = [item.dict() for item in despessas]
        results = batch_create_despessas(items)
        return {"imported_count": len(results), "data": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 3. Filters & Searches
@router.get("/filter", response_model=List[DespesaResponseNested])
async def filter_despesas(
    min_total: Optional[float] = None,
    max_total: Optional[float] = None,
    month: Optional[MonthEnum] = None,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    despesa_like: Optional[str] = None
):
    try:
        filters = {
            "min_total": min_total,
            "max_total": max_total,
            "month": month.value if month else None,
            "min_month_val": min_val,
            "max_month_val": max_val,
            "despesa_like": despesa_like
        }
        return filter_expenses(filters)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sort", response_model=List[DespesaResponseNested])
async def sort_despesas(
    order_by: str = Query("id"),
    direction: SortDirection = SortDirection.ASC
):
    try:
        return sort_expenses(order_by, direction.value)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 4. History
@router.get("/{id}/history")
async def get_history(id: int):
    try:
        return get_despesa_history(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{id}/revert", response_model=DespesaResponseNested)
async def revert_value(id: int, request: RevertRequest):
    try:
        return revert_cell_value(id, request.field, request.version)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 5. Smart Validations
@router.get("/{id}/check-consistency")
async def get_consistency(id: int):
    try:
        return check_consistency(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}/anomalies")
async def get_anomalies(id: int, threshold: float = 200.0):
    try:
        return detect_anomalies(id, threshold)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/validate/duplicates")
async def get_duplicates(name: str = Query(...)):
    try:
        return find_duplicates(name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
