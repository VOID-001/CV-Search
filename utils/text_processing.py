import re
import logging
from models import CVFields
from utils.text_utils import standardize_skills_with_gpt, remove_markdown_formatting
from services.gpt_4o_mini_llm_service import get_response_from_openai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_fields_from_text(text):
    prompt = f"""
    Extract the following information from this CV text:

    Full Name (Title Case)
    Email (Lower Case)
    Contact Number (10 digits Mobile Number)
    Location (State, Title Case)
    Role (Title Case)
    Experience (Decimal Number)
    Skills (Comma Separated Title Case)

    Text:
    {text}
    """

    # Get response from LLM service
    extracted_text = get_response_from_openai(prompt)

    # Remove markdown formatting
    cleaned_text = remove_markdown_formatting(extracted_text)

    # Parse the extracted text to create a CVFields instance
    data = {}
    lines = cleaned_text.split('\n')
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower().replace(' ', '_')
            key = re.sub(r'_+', '_', key)  # Remove multiple underscores
            data[key] = value.strip()

    # Check if all required keys are present and process them
    required_fields = ['full_name', 'email', 'contact_number', 'location', 'role', 'experience', 'skills']
    for field in required_fields:
        if field not in data:
            logger.error(f"Missing required field: {field}")
            raise ValueError(f"Missing required field: {field}")

    # Extract numerical part from experience and convert to float
    experience_str = data['experience']
    experience_value = re.findall(r'\d+\.?\d*', experience_str)
    if experience_value:
        data['experience'] = float(experience_value[0])
    else:
        raise ValueError("Experience value is not in the correct format")
    
    # Standardize skills
    data['skills'] = sorted(standardize_skills_with_gpt([skill.strip() for skill in data['skills'].split(',')]))
    
    # Removing any keys that are not part of the CVFields model
    valid_keys = {'full_name', 'email', 'contact_number', 'location', 'role', 'experience', 'skills'}
    filtered_data = {key: value for key, value in data.items() if key in valid_keys}

    # Creating an instance of CVFields with the filtered data
    cv_fields_instance = CVFields(**filtered_data)

    return cv_fields_instance