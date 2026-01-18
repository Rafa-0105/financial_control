from fastapi import APIRouter, HTTPException, status
from typing import List
from database.connection_db import get_all_users, get_user_by_id
from models.user_schemas import UserResponse

router = APIRouter()

@router.get('/users', response_model=List[UserResponse])
def read_all_users():
    return get_all_users()

@router.get('/users/{user_id}', response_model=UserResponse)
def read_user(user_id: int):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
