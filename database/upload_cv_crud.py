from sqlalchemy.orm import Session
from .models import Skill
from services.ada_002_embedding_service import get_embedding

def get_or_create_skill(db: Session, skill_name: str):
    skill = db.query(Skill).filter(Skill.skill_name == skill_name).first()
    if not skill:
        embedding = get_embedding(skill_name)
        skill = Skill(skill_name=skill_name, vector_embedding=embedding)
        db.add(skill)
        db.commit()
        db.refresh(skill)
    return skill