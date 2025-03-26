from services.ada_002_embedding_service import get_skill_embedding
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
import asyncio

async def process_query_skills(skills):
    query_skills = skills.split(', ')
    query_embeddings = await asyncio.gather(*(get_skill_embedding(skill) for skill in query_skills))

    return query_embeddings


def has_all_skills(metadata, skills):
        return all(skill in set(metadata['skills']) for skill in skills)


async def rerank_skills(skills, query_results):
    query_skills = skills.split(', ')
    skills_set = set(query_skills)
    # reranked_results = sorted(
    #     query_results['matches'],
    #     key=lambda x: (has_all_skills(x['metadata'], skills_set), x['score']),
    #     reverse=True
    # )
    reranked_results = [
        result for result in query_results['matches']
        if has_all_skills(result['metadata'], query_skills)
    ]
    
    reranked_results.sort(key=lambda x: x['score'], reverse=True)

    results = [
        {
            "id": result["id"],
            "score": result["score"],
            "metadata": result["metadata"]
        }
        for result in reranked_results
    ]

    return {"results": results}


