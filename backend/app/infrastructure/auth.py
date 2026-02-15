"""Authentication infrastructure for JWT and password hashing"""
from datetime import datetime, timedelta
from typing import Dict, Any
import logging
import bcrypt
from jose import JWTError, jwt
from app.core import config
from app.common.exceptions import UnauthorizedException, BadRequestException
from app.common.utils import get_pht_now

# Configure logging
logger = logging.getLogger(__name__)


def validate_password(password: str) -> None:
    """
    Validate password meets requirements.
    
    Requirements:
    - At least 8 characters
    - At most 64 characters
    - At most 72 bytes when encoded (bcrypt limit)
    
    Args:
        password: The plaintext password to validate
        
    Raises:
        BadRequestException: If password doesn't meet requirements
    """
    if len(password) < 8:
        logger.warning("Password validation failed: too short")
        raise BadRequestException("Password must be at least 8 characters long")
    
    if len(password) > 64:
        logger.warning("Password validation failed: too long")
        raise BadRequestException("Password must be at most 64 characters long")
    
    # Check byte length (bcrypt has 72 byte limit)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        logger.warning(f"Password validation failed: {len(password_bytes)} bytes exceeds 72 byte limit")
        raise BadRequestException("Password is too long (exceeds 72 bytes when encoded)")
    
    logger.debug(f"Password validation passed (length: {len(password)}, bytes: {len(password_bytes)})")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    
    Validates password length before hashing to prevent bcrypt errors.
    Uses bcrypt directly for better control and error handling.
    
    Args:
        password: The plaintext password to hash
        
    Returns:
        The hashed password string
        
    Raises:
        BadRequestException: If password doesn't meet requirements
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> hashed != "mypassword123"
        True
    """
    # Validate password before hashing
    validate_password(password)
    
    try:
        logger.debug("Hashing password with bcrypt")
        
        # Convert password to bytes
        password_bytes = password.encode('utf-8')
        
        # Ensure we don't exceed bcrypt's 72 byte limit
        if len(password_bytes) > 72:
            logger.warning(f"Truncating password from {len(password_bytes)} to 72 bytes")
            password_bytes = password_bytes[:72]
        
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Convert bytes back to string for storage
        hashed_str = hashed.decode('utf-8')
        
        logger.debug("Password hashed successfully")
        return hashed_str
        
    except ValueError as e:
        logger.error(f"Bcrypt ValueError: {str(e)}")
        raise BadRequestException("Password validation failed. Please use a simpler password.")
    except Exception as e:
        logger.error(f"Password hashing failed: {type(e).__name__}: {str(e)}")
        raise BadRequestException(f"Password hashing failed. Please try again.")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.
    
    Uses bcrypt directly for verification.
    
    Args:
        plain_password: The plaintext password to verify
        hashed_password: The hashed password to verify against
        
    Returns:
        True if the password matches, False otherwise
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    try:
        logger.debug("Verifying password with bcrypt")
        
        # Convert strings to bytes
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Truncate password if needed (same as during hashing)
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        # Verify password
        result = bcrypt.checkpw(password_bytes, hashed_bytes)
        
        logger.debug(f"Password verification result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Password verification failed: {type(e).__name__}: {str(e)}")
        return False


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT access token with expiration.
    
    Args:
        data: Dictionary containing token payload data (e.g., {"sub": user_id, "role": role})
        
    Returns:
        Encoded JWT token string
        
    Example:
        >>> token = create_access_token({"sub": "user123", "role": "admin"})
        >>> isinstance(token, str)
        True
    """
    try:
        to_encode = data.copy()
        expire = get_pht_now() + timedelta(minutes=config.JWT_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        
        logger.debug(f"Creating JWT token for user: {data.get('sub')}")
        encoded_jwt = jwt.encode(
            to_encode,
            config.JWT_SECRET_KEY,
            algorithm=config.JWT_ALGORITHM
        )
        logger.debug("JWT token created successfully")
        
        return encoded_jwt
    except Exception as e:
        logger.error(f"JWT token creation failed: {str(e)}")
        raise


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token string to verify
        
    Returns:
        Dictionary containing the decoded token payload
        
    Raises:
        UnauthorizedException: If the token is invalid, expired, or malformed
        
    Example:
        >>> token = create_access_token({"sub": "user123", "role": "admin"})
        >>> payload = verify_token(token)
        >>> payload["sub"]
        'user123'
    """
    try:
        logger.debug("Verifying JWT token")
        payload = jwt.decode(
            token,
            config.JWT_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM]
        )
        logger.debug(f"JWT token verified for user: {payload.get('sub')}")
        return payload
    except JWTError as e:
        logger.warning(f"JWT token verification failed: {str(e)}")
        raise UnauthorizedException("Could not validate credentials")
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        raise UnauthorizedException("Could not validate credentials")
