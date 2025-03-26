import uuid
from utils.pdf import extract_text_from_pdf
from models import CVFields
from utils.text_processing import extract_fields_from_text  # Assuming additional text processing utilities

async def process_cv_upload(file):
    contents = await file.read()
    pdf_path = f"/tmp/{uuid.uuid4()}.pdf"
    with open(pdf_path, "wb") as f:
        f.write(contents)

    text = extract_text_from_pdf(pdf_path)
    fields = extract_fields_from_text(text)  # Assuming a function that handles this
   
    return fields