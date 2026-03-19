from pydantic import BaseModel, field_validator
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    is_subscribed: Optional[bool] = False

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError("Неверный формат почты")
        return v

    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v is not  None and v <= 0:
            raise ValueError("Возраст должен быть положительным числом")
        return v

class CommonHeaders(BaseModel):
    user_agent: str
    accept_language: str

    @field_validator('accept_language')
    @classmethod
    def validate_accept_language(cls, v):
        if '-' not in v and ',' not in v:
            pass
        return v