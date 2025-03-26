from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import Candidate, Role, CV, Skill, CVSkills
from models import CVFields
import logging

logger = logging.getLogger(__name__)

async def add_candidate(cv_data: CVFields, db: AsyncSession, store_success):
    """Insert a new candidate and their CV into the database only if there isn't one with the same email."""
    try:
        candidate_id = None
        role_id = None

        # Check for existing candidate
        candidate_result = await db.execute(select(Candidate).filter_by(email=cv_data.email))
        candidate = candidate_result.scalars().first()

        if candidate:
            candidate_id = candidate.id  # Capture existing candidate's ID
        else:
            try:
                new_candidate = Candidate(full_name=cv_data.full_name, email=cv_data.email)
                db.add(new_candidate)
                await db.flush()
                candidate_id = new_candidate.id
                candidate = new_candidate
            except IntegrityError as ie:
                await db.rollback()
                logger.error("Failed to add new candidate: %s", ie)
                raise ValueError("Failed to add new candidate due to integrity issues.")

        
        
        # Check for existing role
        role_result = await db.execute(select(Role).filter_by(role=cv_data.role))
        role = role_result.scalars().first()

        if role:
            role_id = role.id  # Capture existing role's ID
        else:
            try:
                new_role = Role(role=cv_data.role)
                db.add(new_role)
                await db.flush()
                role_id = new_role.id
            except IntegrityError as ie:
                await db.rollback()
                logger.error("Failed to add new role: %s", ie)
                raise ValueError("Failed to add new role due to integrity issues.")


        # Check for existing cv
        cv_result = await db.execute(select(CV).filter_by(candidate_id=candidate_id))
        cv = cv_result.scalars().first()

        if cv:
            cv_id = cv.id  # Capture existing cv's ID
        else:
            try:
                new_cv = CV(
                    candidate_id=candidate_id,
                    contact_no=cv_data.contact_number,
                    location=cv_data.location,
                    experience=cv_data.experience,
                    role_id=role_id,
                    stored_in_pinecone=store_success
                )
                db.add(new_cv)
                await db.flush()
                cv_id = new_cv.id
            except IntegrityError as ie:
                await db.rollback()
                logger.error("Failed to add new CV: %s", ie)
                raise ValueError("Failed to add new CV due to integrity issues.")
            
            db.add(new_cv)
            await db.flush()
            cv_id = new_cv.id

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
        
        # Check for existing cv
        cv_skill_results = await db.execute(select(CVSkills).filter_by(cv_id=cv_id))
        existing_skills = {cv_skill.skill_id for cv_skill in cv_skill_results.scalars()}
        if len(existing_skills) == 0:
            for skill_name in skill_names:
                try:
                    skill_result = await db.execute(select(Skill).filter_by(name=skill_name))
                    skill = skill_result.scalars().first()
                    if skill:
                        cv_skill = CVSkills(cv_id=cv_id, skill_id=skill.id)
                        db.add(cv_skill)
                except IntegrityError as ie:
                    await db.rollback()
                    logger.error("Failed to add CV-Skill link for %s: %s", skill_name, ie)
                    raise ValueError(f"Failed to link skill '{skill_name}' to CV due to integrity issues.")

        await db.commit()
        return candidate
    except SQLAlchemyError as e:
        await db.rollback()
        raise e