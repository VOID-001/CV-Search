from pydantic import BaseModel
from typing import List

class CVFields(BaseModel):
    full_name: str
    email: str
    contact_number: str
    location: str
    role: str
    experience: float
    skills: List[str]

class SkillData(BaseModel):
    name: str
    embedding: List[float]
    status: str  
    
class ProcessedSkills(BaseModel):
    status: str

