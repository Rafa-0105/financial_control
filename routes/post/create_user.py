from fastapi import APIRouter, HTTPException, status
import bcrypt
from models.user_schemas import UserCreate, UserResponse
from database.connection_db import create_user_db, get_user_by_email

router = APIRouter()

@router.post('/users', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(user: UserCreate):
    # Check if user already exists
    if get_user_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    try:
        # bcrypt requires bytes
        hashed_bytes = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        hashed_password = hashed_bytes.decode('utf-8') # Store as string
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing password")
    
    # Save to DB
    try:
        new_user = create_user_db(user.username, user.email, hashed_password)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")
    
    return new_user
