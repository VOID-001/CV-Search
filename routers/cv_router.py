from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from services.cv_service import process_cv_upload
from models import CVFields, ProcessedSkills
from security.auth import authenticate, HTTPBasicCredentials
from database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from utils.skill_processing import process_skills
from utils.store_in_pinecone import store_in_pinecone
from services.store_in_pgsql import add_candidate
from typing import Optional
from utils.embeddings_processing import normalize, process_embeddings
from services.pinecone_vector_service import get_pinecone_index
from utils.query_processing import process_query_skills
from utils.query_processing import rerank_skills
import asyncio
import numpy as np
from services.ada_002_embedding_service import get_skill_embedding

router = APIRouter()

@router.post("/extract_cv_details/", response_model=CVFields)
async def upload_cv(file: UploadFile = File(...), credentials: HTTPBasicCredentials = Depends(authenticate)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    return await process_cv_upload(file)


@router.post("/submit_cv/", response_model=ProcessedSkills)
async def submit_cv(cv_data: CVFields, db: AsyncSession = Depends(get_db)):
    try:
        embeddings = await process_skills(cv_data, db)
        if not embeddings:
            raise HTTPException(status_code=400, detail="Failed to generate embeddings")

        normalized_embeddings = process_embeddings(embeddings)
        if normalized_embeddings.size == 0:
            raise HTTPException(status_code=400, detail="Failed to normalize embeddings")

        store_success = store_in_pinecone(cv_data, normalized_embeddings)
        if not store_success:
            raise HTTPException(status_code=500, detail="Failed to store data in Pinecone")

        candidate_result = await add_candidate(cv_data, db, store_success)
        if not candidate_result:
            raise HTTPException(status_code=500, detail="Failed to add candidate")

        return {"status": "Processed"}

    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        print(f"An unexpected error occurred: {str(ex)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during processing")


@router.post("/query_cv/")
async def query_cv(
    skills: str, 
    min_experience: Optional[float] = None,
    max_experience: Optional[float] = None,
    role: Optional[str] = None,
    top_results: int = 25,
    location: Optional[str] = None,
    credentials: HTTPBasicCredentials = Depends(authenticate)
):

    query_embeddings_task = asyncio.create_task(process_query_skills(skills))

    pinecone_index = get_pinecone_index()

    filters = {}
    if min_experience is not None or max_experience is not None:
        filters['experience'] = {}
    if min_experience is not None:
        filters['experience']['$gte'] = min_experience
    if max_experience is not None:
        filters['experience']['$lte'] = max_experience

    if role is not None:
        filters['role'] = {'$eq': role}
    if location is not None:
        filters['location'] = {'$eq': location}

    # Wait for the query_embeddings task to complete
    query_embeddings = await query_embeddings_task
    processed_embeddings = process_embeddings(query_embeddings).tolist()
    
    query_results = pinecone_index.query(
        vector=processed_embeddings,
        top_k=top_results,
        include_metadata=True,
        filter=filters
    )

    result = await rerank_skills(skills, query_results)

    return result
