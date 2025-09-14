from fastapi import Header, HTTPException
from typing import Optional
from firebase_setup import get_user_id_from_token
from models import User

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing.")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Authorization scheme must be Bearer.")
        
        user_id, is_premium = get_user_id_from_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token.")
        
        return User(id=user_id, is_premium=is_premium)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format.")