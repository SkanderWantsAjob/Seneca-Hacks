from pydantic import BaseModel
class User(BaseModel):
    id: str
    is_premium: bool