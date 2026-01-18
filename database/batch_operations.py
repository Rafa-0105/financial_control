from functools import lru_cache
from database.connection_db import get_connection, calculate_total, normalize_keys, format_response_nested
from typing import List, Dict, Any, Optional
from decimal import Decimal

def clear_caches():
    calculate_column_sum.cache_clear()
    calculate_column_average.cache_clear()
    get_monthly_analytics.cache_clear()
    get_top_expenses.cache_clear()

def log_change(cursor, despesa_id: int, field: str, old_value: Optional[float], new_value: Optional[float], user_id: Optional[int]):
    sql = """
        INSERT INTO finacias.despesa_history (despesa_id, field, old_value, new_value, user_id)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (despesa_id, field, old_value, new_value, user_id))

def batch_update_despessas(updates: List[Dict[str, Any]], user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    connection = get_connection()
    results = []
    try:
        with connection.cursor() as cursor:
            for item in updates:
                despesa_id = item.get('id')
                if not despesa_id:
                    continue
                
                # Fetch current values for history and total calculation
                cursor.execute("SELECT * FROM finacias.controle_financeira_teste WHERE id = %s", (despesa_id,))
                current = cursor.fetchone()
                if not current:
                    continue
                
                current = normalize_keys(current)
                
                # Filter out None values and 'id'
                update_fields = {k: v for k, v in item.items() if v is not None and k != 'id'}
                
                if not update_fields:
                    continue
                    
                # Log history for each changed field
                for field, new_val in update_fields.items():
                    old_val = current.get(field.lower())
                    if old_val != new_val:
                        log_change(cursor, despesa_id, field, old_val, new_val, user_id)
                
                # Calculate new total
                merged = current.copy()
                merged.update(update_fields)
                new_total = calculate_total(merged)
                update_fields['total'] = new_total
                
                set_clause = ", ".join([f"{k} = %s" for k in update_fields.keys()])
                sql = f"UPDATE finacias.controle_financeira_teste SET {set_clause} WHERE id = %s"
                cursor.execute(sql, list(update_fields.values()) + [despesa_id])
                
                # Get updated record
                cursor.execute("SELECT * FROM finacias.controle_financeira_teste WHERE id = %s", (despesa_id,))
                updated_record = cursor.fetchone()
                results.append(format_response_nested(normalize_keys(updated_record)))
            
            connection.commit()
            clear_caches()
            return results
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()

def batch_delete_despessas(ids: List[int]) -> int:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            placeholders = ', '.join(['%s'] * len(ids))
            sql = f"DELETE FROM finacias.controle_financeira_teste WHERE id IN ({placeholders})"
            cursor.execute(sql, ids)
            connection.commit()
            clear_caches()
            return cursor.rowcount
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()

def batch_create_despessas(despessas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    connection = get_connection()
    results = []
    try:
        with connection.cursor() as cursor:
            for data in despessas:
                # Calculate total
                data['total'] = calculate_total(data)
                
                insert_data = {k: v for k, v in data.items() 
                              if k not in ['id', 'created_at', 'updated_at']}
                
                columns = ', '.join(insert_data.keys())
                placeholders = ', '.join(['%s'] * len(insert_data))
                sql = f"INSERT INTO finacias.controle_financeira_teste ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, list(insert_data.values()))
                
                despesa_id = cursor.lastrowid
                cursor.execute("SELECT * FROM finacias.controle_financeira_teste WHERE id = %s", (despesa_id,))
                result = cursor.fetchone()
                results.append(format_response_nested(normalize_keys(result)))
            
            connection.commit()
            clear_caches()
            return results
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()

@lru_cache(maxsize=128)
def calculate_column_sum(column: str) -> float:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = f"SELECT SUM({column}) as total FROM finacias.controle_financeira_teste"
            cursor.execute(sql)
            result = cursor.fetchone()
            return float(result['total']) if result and result['total'] else 0.0
    finally:
        connection.close()

@lru_cache(maxsize=128)
def calculate_column_average(column: str) -> float:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = f"SELECT AVG({column}) as average FROM finacias.controle_financeira_teste"
            cursor.execute(sql)
            result = cursor.fetchone()
            return float(result['average']) if result and result['average'] else 0.0
    finally:
        connection.close()

def apply_excel_formula(target_id: int, target_month: str, formula: str, value: float, user_id: Optional[int] = None) -> Dict[str, Any]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT {target_month}, total FROM finacias.controle_financeira_teste WHERE id = %s", (target_id,))
            current = cursor.fetchone()
            if not current:
                raise ValueError("Despesa not found")
            
            old_val = float(current[target_month]) if current[target_month] else 0.0
            new_val = old_val
            
            if formula == "multiply":
                new_val = old_val * value
            elif formula == "divide":
                if value == 0: raise ValueError("Division by zero")
                new_val = old_val / value
            elif formula == "add":
                new_val = old_val + value
            elif formula == "subtract":
                new_val = old_val - value
            elif formula == "percentage":
                new_val = old_val * (value / 100)
            
            # Update record
            cursor.execute(f"UPDATE finacias.controle_financeira_teste SET {target_month} = %s WHERE id = %s", (new_val, target_id))
            
            # Recalculate total
            cursor.execute("SELECT * FROM finacias.controle_financeira_teste WHERE id = %s", (target_id,))
            full_record = normalize_keys(cursor.fetchone())
            new_total = calculate_total(full_record)
            cursor.execute("UPDATE finacias.controle_financeira_teste SET total = %s WHERE id = %s", (new_total, target_id))
            
            log_change(cursor, target_id, target_month, old_val, new_val, user_id)
            
            connection.commit()
            clear_caches()
            
            cursor.execute("SELECT * FROM finacias.controle_financeira_teste WHERE id = %s", (target_id,))
            return format_response_nested(normalize_keys(cursor.fetchone()))
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()

def get_despesa_history(despesa_id: int) -> List[Dict[str, Any]]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM finacias.despesa_history WHERE despesa_id = %s ORDER BY timestamp DESC"
            cursor.execute(sql, (despesa_id,))
            return cursor.fetchall()
    finally:
        connection.close()

def revert_cell_value(despesa_id: int, field: str, version_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Get the value from history
            cursor.execute("SELECT old_value FROM finacias.despesa_history WHERE id = %s AND despesa_id = %s AND field = %s", (version_id, despesa_id, field))
            history_entry = cursor.fetchone()
            if not history_entry:
                raise ValueError("History version not found")
            
            revert_value = history_entry['old_value']
            
            # Get current value for history logging
            cursor.execute(f"SELECT {field} FROM finacias.controle_financeira_teste WHERE id = %s", (despesa_id,))
            current = cursor.fetchone()
            current_val = float(current[field]) if current and current[field] else 0.0
            
            # Update
            cursor.execute(f"UPDATE finacias.controle_financeira_teste SET {field} = %s WHERE id = %s", (revert_value, despesa_id))
            
            # Recalculate total
            cursor.execute("SELECT * FROM finacias.controle_financeira_teste WHERE id = %s", (despesa_id,))
            full_record = normalize_keys(cursor.fetchone())
            new_total = calculate_total(full_record)
            cursor.execute("UPDATE finacias.controle_financeira_teste SET total = %s WHERE id = %s", (new_total, despesa_id))
            
            log_change(cursor, despesa_id, field, current_val, float(revert_value), user_id)
            
            connection.commit()
            clear_caches()
            
            cursor.execute("SELECT * FROM finacias.controle_financeira_teste WHERE id = %s", (despesa_id,))
            return format_response_nested(normalize_keys(cursor.fetchone()))
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()

@lru_cache(maxsize=1)
def get_monthly_analytics() -> Dict[str, float]:
    connection = get_connection()
    meses = ['janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho',
             'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    totals = {}
    try:
        with connection.cursor() as cursor:
            for mes in meses:
                cursor.execute(f"SELECT SUM({mes}) as total FROM finacias.controle_financeira_teste")
                res = cursor.fetchone()
                totals[mes] = float(res['total']) if res and res['total'] else 0.0
            return totals
    finally:
        connection.close()

@lru_cache(maxsize=10)
def get_top_expenses(limit: int = 10) -> List[Dict[str, Any]]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM finacias.controle_financeira_teste ORDER BY total DESC LIMIT %s", (limit,))
            results = cursor.fetchall()
            return [format_response_nested(normalize_keys(r)) for r in results]
    finally:
        connection.close()

def filter_expenses(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = "SELECT * FROM finacias.controle_financeira_teste WHERE 1=1"
            params = []
            
            if filters.get('min_total'):
                query += " AND total >= %s"
                params.append(filters['min_total'])
            if filters.get('max_total'):
                query += " AND total <= %s"
                params.append(filters['max_total'])
            if filters.get('month') and (filters.get('min_month_val') is not None or filters.get('max_month_val') is not None):
                month = filters['month']
                if filters.get('min_month_val') is not None:
                    query += f" AND {month} >= %s"
                    params.append(filters['min_month_val'])
                if filters.get('max_month_val') is not None:
                    query += f" AND {month} <= %s"
                    params.append(filters['max_month_val'])
            if filters.get('despesa_like'):
                query += " AND despesa LIKE %s"
                params.append(f"%{filters['despesa_like']}%")
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [format_response_nested(normalize_keys(r)) for r in results]
    finally:
        connection.close()

def sort_expenses(order_by: str, direction: str) -> List[Dict[str, Any]]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Basic sanitization for order_by
            allowed_cols = ['id', 'despesa', 'total', 'janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
            if order_by.lower() not in allowed_cols:
                order_by = 'id'
            
            dir_str = "DESC" if direction.lower() == "desc" else "ASC"
            sql = f"SELECT * FROM finacias.controle_financeira_teste ORDER BY {order_by} {dir_str}"
            cursor.execute(sql)
            results = cursor.fetchall()
            return [format_response_nested(normalize_keys(r)) for r in results]
    finally:
        connection.close()

def check_consistency(despesa_id: int) -> Dict[str, Any]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM finacias.controle_financeira_teste WHERE id = %s", (despesa_id,))
            record = cursor.fetchone()
            if not record:
                return {"error": "Not found"}
            
            data = normalize_keys(record)
            stored_total = data.get('total', 0.0)
            calculated_total = calculate_total(data)
            
            return {
                "id": despesa_id,
                "stored_total": stored_total,
                "calculated_total": calculated_total,
                "is_consistent": abs(stored_total - calculated_total) < 0.01
            }
    finally:
        connection.close()

def detect_anomalies(despesa_id: int, threshold_percent: float = 200.0) -> List[Dict[str, Any]]:
    # Alert if a monthly value is > threshold_percent of the average monthly value
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM finacias.controle_financeira_teste WHERE id = %s", (despesa_id,))
            record = cursor.fetchone()
            if not record: return []
            
            data = normalize_keys(record)
            meses = ['janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho',
                     'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
            
            values = [float(data[m]) for m in meses if data.get(m)]
            if not values: return []
            
            avg = sum(values) / len(values)
            if avg == 0: return []
            
            anomalies = []
            for m in meses:
                val = float(data[m]) if data.get(m) else 0.0
                percent = (val / avg) * 100
                if percent > threshold_percent:
                    anomalies.append({
                        "month": m,
                        "value": val,
                        "average": round(avg, 2),
                        "percentage_of_avg": round(percent, 2)
                    })
            return anomalies
    finally:
        connection.close()

def find_duplicates(name: str) -> List[Dict[str, Any]]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Simple LIKE check for similar names
            sql = "SELECT * FROM finacias.controle_financeira_teste WHERE despesa LIKE %s"
            cursor.execute(sql, (f"%{name}%",))
            results = cursor.fetchall()
            return [format_response_nested(normalize_keys(r)) for r in results]
    finally:
        connection.close()
