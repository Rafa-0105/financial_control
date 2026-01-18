from fastapi import APIRouter, HTTPException, status
import bcrypt
from typing import Optional
from database.connection_db import update_user, get_user_by_email
from models.user_schemas import UserUpdate, UserResponse

router = APIRouter()

@router.put('/users/{user_id}', response_model=UserResponse)
def update_user_endpoint(user_id: int, user: UserUpdate):
    data = user.model_dump(exclude_unset=True)
    
    # Handle password hashing if present
    if 'password' in data and data['password']:
        try:
            hashed_bytes = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            data['password_hash'] = hashed_bytes.decode('utf-8')
            del data['password']
        except Exception:
            raise HTTPException(status_code=500, detail="Error processing password")
            
    # Check email uniqueness if email is being updated
    if 'email' in data:
        existing_user = get_user_by_email(data['email'])
        if existing_user and existing_user['id'] != user_id:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    updated_user = update_user(user_id, data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    return updated_user
