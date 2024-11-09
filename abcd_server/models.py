from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., regex="^[\w\.-]+@[\w\.-]+\.\w{2,4}$")
    full_name: str = Field(..., min_length=1)
    age: int = Field(..., ge=0, le=120)

    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "age": 30,
            }
        }
