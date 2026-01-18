import json, urllib.request
from typing import Optional
from fastapi import HTTPException
from jose import jwt, jwk
from jose.exceptions import JWTError

from app.core_app.config import settings

JWKS_URL = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
_jwks_cache = None

def _get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        try:
            with urllib.request.urlopen(JWKS_URL, timeout=10) as r:
                _jwks_cache = json.load(r)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Failed to fetch JWKS: {e}")
    return _jwks_cache

def get_user_id_from_auth(authorization: Optional[str]) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.split(" ", 1)[1].strip()

    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        alg = header.get("alg", "ES256")

        jwks = _get_jwks()
        jwk_dict = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        if not jwk_dict:
            raise HTTPException(status_code=401, detail="Unknown token key (kid)")

        key = jwk.construct(jwk_dict, algorithm=alg)
        payload = jwt.decode(
            token,
            key.to_pem().decode("utf-8"),
            algorithms=[alg],
            options={"verify_aud": False},
        )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing sub")
        return user_id

    except HTTPException:
        raise
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
