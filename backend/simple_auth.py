#!/usr/bin/env python3
"""
Simple in-memory authentication for AJ Institute SATS AI Co-Pilot
Temporary solution until database is properly configured
"""

import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from jose import JWTError, jwt
import os

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "Ghanashyama@2103")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12

# In-memory user store (temporary solution)
USERS_DB = {
    "ajadmin": {
        "id": 1,
        "username": "ajadmin",
        "password_hash": hashlib.sha256("AJTriage2024!".encode()).hexdigest(),
        "full_name": "AJ Admin",
        "role": "admin",
        "is_active": True
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user with username and password"""
    user = USERS_DB.get(username)
    if not user:
        return None
    
    if not user["is_active"]:
        return None
    
    if not verify_password(password, user["password_hash"]):
        return None
    
    # Return user data without password hash
    user_data = user.copy()
    del user_data["password_hash"]
    return user_data

def create_user_token(user_data: Dict[str, Any]) -> str:
    """Create a JWT token for a user"""
    token_data = {
        "user_id": user_data["id"],
        "username": user_data["username"],
        "role": user_data["role"],
        "full_name": user_data["full_name"]
    }
    return create_access_token(token_data)

def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """Get user data from JWT token"""
    try:
        payload = verify_token(token)
        username = payload.get("username")
        if username and username in USERS_DB:
            user_data = USERS_DB[username].copy()
            del user_data["password_hash"]
            return user_data
        return None
    except:
        return None