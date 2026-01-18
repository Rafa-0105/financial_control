from fastapi import APIRouter, HTTPException, status
from database.connection_db import delete_user

router = APIRouter()

@router.delete('/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(user_id: int):
    if not delete_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None
