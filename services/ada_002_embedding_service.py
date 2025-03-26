import logging
from openai import OpenAI
import os
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load environment variables from .env file
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.error("OPENAI_API_KEY is not set in the environment.")
    raise EnvironmentError("OPENAI_API_KEY is not set in the environment.")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

async def get_skill_embedding(skill_name: str) -> list:
    """Generate a vector embedding for a skill using OpenAI."""
    try:
        response = client.embeddings.create(
            input=skill_name,
            model="text-embedding-ada-002"
        )
        # Extract the first embedding vector
        return np.array(response.data[0].embedding)
    except Exception as e:
        print(f"Failed to generate embedding: {e}")
        return []