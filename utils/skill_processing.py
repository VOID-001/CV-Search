from database.models import Skill
from services.ada_002_embedding_service import get_skill_embedding
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import SkillData
import numpy as np

async def process_skills(cv_data, db: AsyncSession):
    embeddings = []
    skills_info = []
    # Check if the skills are provided in a single string or already as a list
    if isinstance(cv_data.skills, list) and len(cv_data.skills) == 1 and ',' in cv_data.skills[0]:
        # Handle single string in a list which contains comma-separated values
        skill_names = [skill.strip() for skill in cv_data.skills[0].split(',')]
    elif isinstance(cv_data.skills, list):
        # Handle list of strings
        skill_names = [skill.strip() for skill in cv_data.skills]
    else:
        # If it's neither, raise an error or handle it as a malformed input
        raise ValueError("Skills input is not properly formatted")
    
    for skill_name in skill_names:
        # Check if the skill already exists in the database
        result = await db.execute(select(Skill).filter(Skill.name == skill_name))
        skill = result.scalars().first()
        if not skill:
            # Fetch embedding asynchronously
            embedding = await get_skill_embedding(skill_name)
            # Create a new Skill object and add it to the session
            skill = Skill(name=skill_name, vector_embedding=embedding)
            db.add(skill)
            try:
                await db.commit()
                await db.refresh(skill)
                embeddings.append(embedding)
                skills_info.append(SkillData(name=skill_name, embedding=embedding, status="new"))
            except SQLAlchemyError as e:
                await db.rollback()
                raise HTTPException(status_code=500, detail=str(e))
        else:
            embeddings.append(skill.vector_embedding)
            skills_info.append(SkillData(name=skill_name, embedding=skill.vector_embedding, status="existing"))

    return embeddings

