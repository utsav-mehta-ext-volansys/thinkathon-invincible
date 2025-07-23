from pydantic import BaseModel, EmailStr, Field, validator


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    confirm_password: str

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    full_name: str
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse