from __future__ import annotations
import datetime as dt
from typing import Any, Dict, Optional

import jwt


class JWTManager:
    def __init__(
        self,
        algorithm: str,
        secret: Optional[str] = None,
        private_key_path: Optional[str] = None,
        public_key_path: Optional[str] = None,
    ) -> None:
        self.algorithm = algorithm
        self.secret = secret
        self.private_key = None
        self.public_key = None
        if private_key_path:
            with open(private_key_path, "r", encoding="utf-8") as f:
                self.private_key = f.read()
        if public_key_path:
            with open(public_key_path, "r", encoding="utf-8") as f:
                self.public_key = f.read()

    def _get_signing_key(self) -> str:
        if self.algorithm.startswith("HS"):
            if not self.secret:
                raise ValueError("JWT_SECRET is required for HS algorithms")
            return self.secret
        # RS algorithms
        if not self.private_key:
            raise ValueError("JWT_PRIVATE_KEY_PATH is required for RS algorithms")
        return self.private_key

    def _get_verification_key(self) -> str:
        if self.algorithm.startswith("HS"):
            if not self.secret:
                raise ValueError("JWT_SECRET is required for HS algorithms")
            return self.secret
        if not self.public_key:
            # If public key not set, allow using private key for verification in single-key setups
            if self.private_key:
                return self.private_key
            raise ValueError("JWT_PUBLIC_KEY_PATH is required for RS algorithms")
        return self.public_key

    def encode(self, payload: Dict[str, Any], expires_in_seconds: int) -> str:
        now = dt.datetime.utcnow()
        payload = {
            **payload,
            "iat": now,
            "exp": now + dt.timedelta(seconds=expires_in_seconds),
        }
        return jwt.encode(payload, self._get_signing_key(), algorithm=self.algorithm)

    def decode(self, token: str) -> Dict[str, Any]:
        return jwt.decode(token, self._get_verification_key(), algorithms=[self.algorithm])
