from pydantic import BaseModel

class RequireID(BaseModel):
    _id: str