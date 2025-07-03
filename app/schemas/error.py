from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    code: int
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "code": 400,
                "message": "Invalid input"
            }
        }
