from fastapi import APIRouter, HTTPException, status
from typing import Dict, List
import uuid
from datetime import datetime

from weather_alerts.models.user import User, UserCreate, UserUpdate

router = APIRouter()

# Temporary in-memory storage (we'll replace with DynamoDB later)
users_db: Dict[str, User] = {}


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """
    Register a new user with weather alert preferences.

    - **email**: User's email address
    - **location**: City name (e.g., "Berlin,DE") or coordinates
    - **preferences**: Alert thresholds and settings
    """
    # Check if email already exists
    for existing_user in users_db.values():
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

    user_id = str(uuid.uuid4())

    user = User(
        user_id=user_id,
        email=user_data.email,
        location=user_data.location,
        preferences=user_data.preferences,
        created_at=datetime.utcnow(),
        last_alert=None
    )

    users_db[user_id] = user
    return user


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user details by ID"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return users_db[user_id]


@router.get("/", response_model=List[User])
async def list_users(limit: int = 100, offset: int = 0):
    """
    List all users with pagination.

    - **limit**: Maximum number of users to return (default 100)
    - **offset**: Number of users to skip (default 0)
    """
    all_users = list(users_db.values())
    return all_users[offset:offset + limit]


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, update_data: UserUpdate):
    """
    Update user preferences or location.

    Only provided fields will be updated.
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user = users_db[user_id]

    # Update only provided fields
    if update_data.location is not None:
        user.location = update_data.location
    if update_data.preferences is not None:
        user.preferences = update_data.preferences

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    """Delete a user by ID"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    del users_db[user_id]
    return None