import logging
from openai import OpenAI
import os

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

def get_response_from_openai(prompt):
    """Send a prompt to OpenAI and return the response."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts information from CVs."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5
    )
    extracted_text = response.choices[0].message.content.strip()
    # logger.info(f"Extracted text: {extracted_text}")
    return extracted_text