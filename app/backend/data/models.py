from typing import Optional
from pydantic import BaseModel


class ScientificAbstract(BaseModel):
    doi: Optional[str]
    title: Optional[str]
    authors: Optional[str]
    year: Optional[int]
    abstract_content: str
    
class UserQueryRecord(BaseModel):
    user_query_id: str
    user_query: str