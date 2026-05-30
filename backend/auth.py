"""
Authentication and Authorization for AJ Institute SATS AI Co-Pilot
JWT-based authentication with role-based access control
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import logging

from database import get_db
from models import UserRole

# Configure logging
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass


class AuthorizationError(Exception):
    """Custom exception for authorization errors"""
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a plain password
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation error: {e}")
        raise AuthenticationError("Failed to create access token")


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        raise AuthenticationError("Invalid or expired token")


def authenticate_user(db: Session, username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user with username and password
    
    Args:
        db: Database session
        username: Username
        password: Plain text password
        
    Returns:
        User data if authentication successful, None otherwise
    """
    try:
        # Import here to avoid circular imports
        from sqlalchemy import text
        
        # Query user from database
        result = db.execute(
            text("SELECT id, username, password_hash, full_name, role, is_active FROM users WHERE username = :username"),
            {"username": username}
        )
        user_row = result.fetchone()
        
        if not user_row:
            logger.warning(f"Authentication failed: User {username} not found")
            return None
        
        user_data = {
            "id": user_row[0],
            "username": user_row[1],
            "password_hash": user_row[2],
            "full_name": user_row[3],
            "role": user_row[4],
            "is_active": user_row[5]
        }
        
        # Check if user is active
        if not user_data["is_active"]:
            logger.warning(f"Authentication failed: User {username} is inactive")
            return None
        
        # Verify password
        if not verify_password(password, user_data["password_hash"]):
            logger.warning(f"Authentication failed: Invalid password for user {username}")
            return None
        
        # Remove password hash from returned data
        del user_data["password_hash"]
        
        logger.info(f"User {username} authenticated successfully")
        return user_data
        
    except Exception as e:
        logger.error(f"Authentication error for user {username}: {e}")
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        Current user data
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = verify_token(credentials.credentials)
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        
        if user_id is None or username is None:
            raise credentials_exception
        
        # Get user from database
        from sqlalchemy import text
        result = db.execute(
            text("SELECT id, username, full_name, role, is_active FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        )
        user_row = result.fetchone()
        
        if not user_row:
            raise credentials_exception
        
        user_data = {
            "id": user_row[0],
            "username": user_row[1],
            "full_name": user_row[2],
            "role": user_row[3],
            "is_active": user_row[4]
        }
        
        # Check if user is still active
        if not user_data["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        return user_data
        
    except AuthenticationError:
        raise credentials_exception
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise credentials_exception


def require_role(allowed_roles: list[UserRole]):
    """
    Dependency factory to require specific user roles
    
    Args:
        allowed_roles: List of allowed user roles
        
    Returns:
        Dependency function
    """
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role")
        
        if user_role not in [role.value for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in allowed_roles]}"
            )
        
        return current_user
    
    return role_checker


def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency to require admin role
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user data if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_consultant_or_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency to require consultant or admin role
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user data if consultant or admin
        
    Raises:
        HTTPException: If user is not consultant or admin
    """
    allowed_roles = [UserRole.CONSULTANT.value, UserRole.ADMIN.value]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consultant or Admin access required"
        )
    return current_user


def can_access_case(current_user: Dict[str, Any], case_nurse_id: int) -> bool:
    """
    Check if current user can access a specific case
    
    Args:
        current_user: Current authenticated user
        case_nurse_id: ID of the nurse who created the case
        
    Returns:
        True if user can access the case, False otherwise
    """
    user_role = current_user.get("role")
    user_id = current_user.get("id")
    
    # Admins and consultants can access all cases
    if user_role in [UserRole.ADMIN.value, UserRole.CONSULTANT.value]:
        return True
    
    # Nurses can only access their own cases
    if user_role == UserRole.TRIAGE_NURSE.value:
        return user_id == case_nurse_id
    
    return False


def log_authentication_event(
    db: Session,
    user_id: Optional[int],
    action: str,
    success: bool,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    Log authentication events for audit purposes
    
    Args:
        db: Database session
        user_id: User ID (if known)
        action: Action performed (login, logout, etc.)
        success: Whether the action was successful
        ip_address: Client IP address
        user_agent: Client user agent
        details: Additional details
    """
    try:
        from sqlalchemy import text
        
        audit_details = {
            "action": action,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        if details:
            audit_details.update(details)
        
        db.execute(
            text("""
                INSERT INTO audit_log (user_id, action, details, ip_address, user_agent)
                VALUES (:user_id, :action, :details, :ip_address, :user_agent)
            """),
            {
                "user_id": user_id,
                "action": f"AUTH_{action.upper()}",
                "details": audit_details,
                "ip_address": ip_address,
                "user_agent": user_agent
            }
        )
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to log authentication event: {e}")


def create_user_token(user_data: Dict[str, Any]) -> str:
    """
    Create a JWT token for a user
    
    Args:
        user_data: User data from database
        
    Returns:
        JWT token string
    """
    token_data = {
        "user_id": user_data["id"],
        "username": user_data["username"],
        "role": user_data["role"],
        "full_name": user_data["full_name"]
    }
    
    return create_access_token(token_data)


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors


# Example usage and testing
if __name__ == "__main__":
    # Test password hashing
    test_password = "TestPassword123!"
    hashed = get_password_hash(test_password)
    print(f"Original: {test_password}")
    print(f"Hashed: {hashed}")
    print(f"Verification: {verify_password(test_password, hashed)}")
    
    # Test token creation
    test_user_data = {
        "user_id": 1,
        "username": "testuser",
        "role": "admin",
        "full_name": "Test User"
    }
    
    token = create_access_token(test_user_data)
    print(f"Token: {token}")
    
    # Test token verification
    try:
        decoded = verify_token(token)
        print(f"Decoded: {decoded}")
    except AuthenticationError as e:
        print(f"Token verification failed: {e}")
    
    # Test password strength validation
    weak_passwords = ["123", "password", "Password", "Password123"]
    strong_password = "StrongPass123!"
    
    for pwd in weak_passwords + [strong_password]:
        is_valid, errors = validate_password_strength(pwd)
        print(f"Password '{pwd}': {'✅ Valid' if is_valid else '❌ Invalid'}")
        if errors:
            for error in errors:
                print(f"  - {error}")