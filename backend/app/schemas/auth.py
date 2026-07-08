from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "engineer"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
