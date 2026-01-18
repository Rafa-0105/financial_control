from fastapi import APIRouter, HTTPException, status
import bcrypt
from models.user_schemas import UserLogin
from database.connection_db import get_user_by_email

router = APIRouter()

@router.post('/login')
def login(user_credentials: UserLogin):
    user = get_user_by_email(user_credentials.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    try:
        if not bcrypt.checkpw(user_credentials.password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    except Exception as e:
        # If encoding fails or format is wrong
        print(f"Login verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return {"message": "Login successful", "user_id": user['id'], "username": user['username']}
