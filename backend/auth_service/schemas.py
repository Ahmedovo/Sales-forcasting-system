from __future__ import annotations
from dataclasses import dataclass


@dataclass
class RegisterRequest:
    name: str
    email: str
    password: str
    role: str


@dataclass
class LoginRequest:
    email: str
    password: str
