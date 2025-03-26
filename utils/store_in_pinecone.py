from services.pinecone_vector_service import get_pinecone_index
import logging

def store_in_pinecone(cv_data, embedding):
    try:
        pinecone_index = get_pinecone_index()
        
        metadata = {
            "role": cv_data.role,
            "email": cv_data.email,
            "contact_number": cv_data.contact_number,
            "location": cv_data.location,
            "experience": cv_data.experience,
            "skills": cv_data.skills
        }

        # Assuming pinecone_index is already initialized and connected
        pinecone_index.upsert(vectors=[(metadata['full_name'], embedding, metadata)])
        return True
    except Exception as e:
        logging.error(f"Failed to upsert data to Pinecone: {e}")
        return False