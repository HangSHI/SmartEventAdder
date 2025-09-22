"""
Authentication module for Gmail Add-on API

Handles Google Identity Token (OIDC) validation for Apps Script requests.
"""

import logging
from typing import Optional
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import requests
from functools import lru_cache

logger = logging.getLogger(__name__)

# Security scheme for Bearer token authentication
security = HTTPBearer(auto_error=False)

# Google's public key endpoint for JWT verification
GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_TOKEN_INFO_URL = "https://oauth2.googleapis.com/tokeninfo"

@lru_cache(maxsize=1)
def get_google_public_keys():
    """
    Fetch and cache Google's public keys for JWT verification.
    """
    try:
        response = requests.get(GOOGLE_CERTS_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch Google public keys: {str(e)}")
        return None

def verify_google_token(token: str) -> Optional[dict]:
    """
    Verify Google Identity Token (OIDC) from Apps Script.

    Args:
        token: The OIDC token from ScriptApp.getIdentityToken()

    Returns:
        Dict with token payload if valid, None if invalid
    """
    try:
        # Method 1: Use Google's tokeninfo endpoint for verification
        # This is simpler but requires an external API call
        response = requests.get(
            GOOGLE_TOKEN_INFO_URL,
            params={'id_token': token},
            timeout=10
        )

        if response.status_code == 200:
            token_info = response.json()

            # Verify the token is issued by Google
            if token_info.get('iss') not in ['accounts.google.com', 'https://accounts.google.com']:
                logger.warning("Token not issued by Google")
                return None

            # Check if token is expired
            if 'exp' in token_info:
                import time
                if int(token_info['exp']) < time.time():
                    logger.warning("Token has expired")
                    return None

            logger.info(f"Token verified for user: {token_info.get('email', 'unknown')}")
            return token_info
        else:
            logger.warning(f"Token verification failed: {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[dict]:
    """
    FastAPI dependency to get current authenticated user from OIDC token.

    Args:
        credentials: Authorization header credentials

    Returns:
        User info dict if authenticated, None if not
    """
    if not credentials:
        return None

    token_info = verify_google_token(credentials.credentials)
    if not token_info:
        return None

    return {
        'email': token_info.get('email'),
        'name': token_info.get('name'),
        'picture': token_info.get('picture'),
        'verified_email': token_info.get('email_verified', False)
    }

async def require_authentication(user: dict = Depends(get_current_user)) -> dict:
    """
    FastAPI dependency that requires authentication.
    Raises HTTPException if user is not authenticated.

    Args:
        user: User info from get_current_user dependency

    Returns:
        User info dict

    Raises:
        HTTPException: 401 if not authenticated
    """
    if not user:
        logger.warning("Authentication required but no valid token provided")
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide a valid Google Identity Token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user

async def optional_authentication(user: dict = Depends(get_current_user)) -> Optional[dict]:
    """
    FastAPI dependency for optional authentication.
    Returns user info if authenticated, None if not (without raising error).

    Args:
        user: User info from get_current_user dependency

    Returns:
        User info dict if authenticated, None if not
    """
    return user

# Development mode - allows requests without authentication
DEVELOPMENT_MODE = False  # Set to True for development testing

async def development_auth_bypass(request: Request) -> bool:
    """
    Check if request should bypass authentication in development mode.

    Args:
        request: FastAPI Request object

    Returns:
        True if authentication should be bypassed, False otherwise
    """
    if not DEVELOPMENT_MODE:
        return False

    # Check if request is from localhost
    client_host = getattr(request.client, 'host', '')
    if client_host in ['127.0.0.1', 'localhost']:
        logger.info("Development mode: bypassing authentication for localhost")
        return True

    return False

async def flexible_authentication(
    request: Request,
    user: dict = Depends(get_current_user)
) -> Optional[dict]:
    """
    Flexible authentication that allows development bypass.

    Args:
        request: FastAPI Request object
        user: User info from get_current_user dependency

    Returns:
        User info dict if authenticated or in development mode, None otherwise
    """
    # Check development bypass
    if await development_auth_bypass(request):
        return {
            'email': 'dev@localhost',
            'name': 'Development User',
            'picture': None,
            'verified_email': True
        }

    return user