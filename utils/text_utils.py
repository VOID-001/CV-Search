import os
import re
import logging
from spacy import load
from services.gpt_4o_mini_llm_service import get_response_from_openai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


nlp = load('en_core_web_sm')  # Load spaCy's English language model once

def standardize_skills_with_gpt(skills):
    prompt = f"""
    Please standardize the following list of skills and return them as a comma-separated list:

    {', '.join(skills)}

    The standardized skills should be formatted correctly with appropriate capitalization and spacing.
    """

    standardized_skills_text = get_response_from_openai(prompt)
    standardized_skills = [skill.strip() for skill in standardized_skills_text.split(',')]
    
    return standardized_skills


def remove_markdown_formatting(text):
    # Remove markdown formatting such as ** and **
    cleaned_text = re.sub(r'[\*\-]+', '', text)
    return cleaned_text