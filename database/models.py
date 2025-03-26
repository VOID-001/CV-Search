from sqlalchemy import Column, Integer, String, Float, ARRAY, DateTime, Float, func, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates, relationship

Base = declarative_base()

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    vector_embedding = Column(ARRAY(Float))
    created_date = Column(DateTime, default=func.now())
    modified_date = Column(DateTime, onupdate=func.now())
    skills = relationship("CVSkills", back_populates="skill")

class Candidate(Base):
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    modified_date = Column(DateTime(timezone=True), onupdate=func.now())
    cvs = relationship("CV", back_populates="candidate")

    @validates('email')
    def validate_email(self, key, address):
        assert '@' in address, "Invalid email address"
        return address
    

class CV(Base):
    __tablename__ = 'cvs'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    contact_no = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    experience = Column(Float, nullable=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    stored_in_pinecone = Column(Boolean, default=False, nullable=False)
    created_date = Column(DateTime, default=func.now())
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    candidate = relationship("Candidate", back_populates="cvs")
    skills = relationship("CVSkills", back_populates="cv")
    role = relationship("Role", back_populates="cvs")


class CVSkills(Base):
    __tablename__ = 'cv_skills'
    
    id = Column(Integer, primary_key=True)
    cv_id = Column(Integer, ForeignKey('cvs.id'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skills.id'), nullable=False)
    created_date = Column(DateTime, default=func.now())
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    cv = relationship("CV", back_populates="skills")
    skill = relationship("Skill", back_populates="skills")


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    role = Column(String(255), nullable=False)
    cvs = relationship("CV", back_populates="role")