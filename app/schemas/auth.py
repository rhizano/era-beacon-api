from pydantic import BaseModel


class UserRegistration(BaseModel):
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "SecureP@ssw0rd123"
            }
        }


class UserLogin(BaseModel):
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "SecureP@ssw0rd123"
            }
        }


class AuthSuccess(BaseModel):
    token: str

    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c2VyMTIzIiwiaWF0IjoxNjQ2MTQ0MDAwLCJleHAiOjE2NDYxNDc2MDB9.EXAMPLE_JWT_TOKEN"
            }
        }


class TokenData(BaseModel):
    user_id: str = None
