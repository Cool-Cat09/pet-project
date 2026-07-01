import jwt
from typing import Any
from datetime import datetime, timedelta, timezone

from api_config import jwt_settings

def encode_jwt(
        payload: dict[Any, Any],
        private_key: str = jwt_settings.read_private_key,
        algorithm: str = jwt_settings.algorithm,
        expire_minutes: int = jwt_settings.access_token_expire
):
    """encoding data using the private key
    
    return: JWT
    """
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    expire = timedelta(minutes=expire_minutes) + now
    to_encode.update(exp=expire, iat=now)
    encoded = jwt.encode(payload=to_encode, key=private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
        token: str | bytes,
        public_key: str = jwt_settings.read_public_key,
        algorithm: str = jwt_settings.algorithm,
):
    """decoding public key
    
    return: payload
    """


    decoded = jwt.decode(jwt=token, key=public_key, algorithms=algorithm)
    return decoded