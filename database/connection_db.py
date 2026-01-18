import pymysql.cursors
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any, cast 
from decimal import Decimal

load_dotenv()

def normalize_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    """Converte chaves para minúsculo E calcula total"""
    if not data:
        return {}
    
    normalized = {k.lower(): v for k, v in data.items()}
    
    normalized['total'] = calculate_total(normalized)
    
    return normalized

def format_response_nested(data: Dict[str, Any]) -> Dict[str, Any]:
    """Formats the flat dictionary into the nested structure."""
    if not data:
        return {}
    
    monthly_data = {
        k: data.get(k, 0.0) for k in [
            'janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho',
            'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
        ]
    }
    
    return {
        "id": data.get('id'),
        "despesa": data.get('despesa'),
        "monthly_data": monthly_data,
        "annual_total": data.get('total', 0.0)
    }

def normalize_keys_list(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Converte chaves de lista para minúsculo"""
    if not data_list:
        return []
    # Normalize then format
    return [format_response_nested(normalize_keys(item)) for item in data_list]


def get_connection() -> pymysql.connections.Connection:
    return pymysql.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME'],
        charset=os.environ['DB_CHARSET'],
        cursorclass=pymysql.cursors.DictCursor
    )

def calculate_total(data: Dict[str, Any]) -> float:
    """Calcula o total de todos os meses"""
    meses = ['janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho',
             'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    
    total = 0.0
    for mes in meses:
        valor = data.get(mes)
        if valor is not None:
            if isinstance(valor, Decimal):
                total += float(valor)
            elif isinstance(valor, str):
                try:
                    # Clean string: remove R$, spaces, dots (thousands), replace comma with dot
                    clean_valor = valor.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
                    if not clean_valor:
                        continue
                    total += float(clean_valor)
                except ValueError:
                    # If conversion fails, assume 0
                    total += 0.0
            else:
                total += float(valor)
    
    return round(total, 2)

def create_despesa(data: Dict[str, Any]) -> Dict[str, Any]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Calculate total before inserting
            data['total'] = calculate_total(data)
            
            insert_data = {k: v for k, v in data.items() 
                          if k not in ['id', 'created_at', 'updated_at']}
            
            columns = ', '.join(insert_data.keys())
            placeholders = ', '.join(['%s'] * len(insert_data))
            sql = f"INSERT INTO finacias.controle_financeira_teste ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, list(insert_data.values()))
            connection.commit()
            
            despesa_id = cursor.lastrowid
            cursor.execute("SELECT * FROM finacias.controle_financeira_teste WHERE id = %s", (despesa_id,))
            result = cursor.fetchone()
            
            return format_response_nested(normalize_keys(cast(Dict[str, Any], result)))
    finally:
        connection.close()

def get_all_despesas() -> List[Dict[str, Any]]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM finacias.controle_financeira_teste ORDER BY id DESC")
            result = cursor.fetchall()
            return normalize_keys_list(cast(List[Dict[str, Any]], result)) if result else []
    finally:
        connection.close()

def get_despesa_by_id(despesa_id: int) -> Optional[Dict[str, Any]]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM finacias.controle_financeira_teste WHERE id = %s", (despesa_id,))
            result = cursor.fetchone()
            return format_response_nested(normalize_keys(cast(Dict[str, Any], result))) if result else None
    finally:
        connection.close()

def update_despesa(despesa_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Get current data to merge (using internal get to avoid nested format loop if called recursively, but here we call public which formats... wait.
            # actually we need raw data for update logic.
            # FIX: get_despesa_by_id now returns nested. This breaks update logic which expects flat dict keys.
            # I must separate "get for logic" vs "get for api".
            # Or I can fix update_despesa to expect nested or re-flatten.
            # Better approach: Create logical_get_despesa_by_id (flat) and public_get_despesa_by_id (nested).
            # For now, let's reverse the format in update or just query directly.
            
            cursor.execute("SELECT * FROM finacias.controle_financeira_teste WHERE id = %s", (despesa_id,))
            current_raw = cursor.fetchone()
            
            if current_raw is None:
                return None
            
            despesa_atual = normalize_keys(cast(Dict[str, Any], current_raw))

            # Merge current data with updates to calculate new total
            merged_data = despesa_atual.copy()
            merged_data.update({k: v for k, v in data.items() if v is not None})
            
            # Calculate new total
            new_total = calculate_total(merged_data)
            
            # Prepare update data including total
            update_data = {k: v for k, v in data.items() 
                          if v is not None and k not in ['id', 'total']}
            
            # Always update total
            update_data['total'] = new_total
            
            set_clause = ', '.join([f"{k} = %s" for k in update_data.keys()])
            sql = f"UPDATE finacias.controle_financeira_teste SET {set_clause} WHERE id = %s"
            cursor.execute(sql, list(update_data.values()) + [despesa_id])
            connection.commit()
            
            # Return nested
            cursor.execute("SELECT * FROM finacias.controle_financeira_teste WHERE id = %s", (despesa_id,))
            result = cursor.fetchone()
            return format_response_nested(normalize_keys(cast(Dict[str, Any], result))) if result else None
    finally:
        connection.close()


def delete_despesa(despesa_id: int) -> bool:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM finacias.controle_financeira_teste WHERE id = %s", (despesa_id,))
            connection.commit()
            return cursor.rowcount > 0
    finally:
        connection.close()

def init_db():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Create Users Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS finacias.users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            connection.commit()
    finally:
        connection.close()

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM finacias.users WHERE email = %s", (email,))
            result = cursor.fetchone()
            return result
    finally:
        connection.close()

def create_user_db(username: str, email: str, password_hash: str) -> Dict[str, Any]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO finacias.users (username, email, password_hash) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, email, password_hash))
            connection.commit()
            
            user_id = cursor.lastrowid
            
            return {
                "id": user_id,
                "username": username,
                "email": email
            }
    finally:
        connection.close()


