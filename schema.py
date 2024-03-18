from pydantic import BaseModel
# 
# 
# Modelo Pydantic para validação
class UserCreate(BaseModel):
    name: str
    email: str