import os
import time
import json
import tempfile
import io
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv
from fpdf import FPDF

# Load environment variables
load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")  # ✅ Consistent naming
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")
AZURE_ASSISTANT_ID = os.getenv("AZURE_ASSISTANT_ID")

# Ensure all required env variables are set
missing_vars = [var for var in ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_KEY", "VECTOR_STORE_ID", "AZURE_ASSISTANT_ID"] if not globals()[var]]
if missing_vars:
    raise ValueError(f"❌ Missing required environment variables: {', '.join(missing_vars)}")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-05-01-preview"
)

# Initialize FastAPI
app = FastAPI()

# ✅ Function: Retrieve relevant experience from vector store
def retrieve_relevant_experience(job_description):
    """Simulates retrieving relevant experience from a vector store"""
    return [
        f"Experience 1 related to {job_description}",
        f"Experience 2 related to {job_description}"
    ]

# ✅ Function: Generate resume using Assistant
async def generate_resume(job_description: str, applicant_details: str) -> str:
    """Uses Azure OpenAI Assistant to generate a resume."""
    try:
        retrieved_experience = retrieve_relevant_experience(job_description)

        # Create a new thread
        thread = client.beta.threads.create()

        # Send user input to the Assistant
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Generate a resume for:\n\n👤 **Applicant Details:**\n{applicant_details}\n\n📝 **Job Description:**\n{job_description}\n\n📂 **Relevant Experience Retrieved:**\n{retrieved_experience}"
        )

        # Run the Assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=AZURE_ASSISTANT_ID
        )

        # Loop until completion
        while run.status in ['queued', 'in_progress']:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        # Handle the response
        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            return messages[0]["content"]

        elif run.status == 'requires_action':
            return "⚠️ Assistant requires additional processing."

        else:
            return f"❌ Assistant failed with status: {run.status}"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume generation failed: {str(e)}")

# ✅ Function: Save resume as PDF with Unicode Support
async def save_pdf(text: str) -> str:
    """Saves the generated resume as a PDF with Unicode font support."""
    
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", '', 12)
            self.cell(0, 10, "Generated Resume", 0, 1, "C")

        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", '', 8)
            self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

        def chapter_title(self, title):
            self.set_font("Arial", '', 14)
            self.cell(0, 10, title, 0, 1, "L")
            self.ln(5)

        def chapter_body(self, body):
            self.set_font("Arial", '', 12)
            self.multi_cell(0, 10, body)
            self.ln()

    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title("Resume")
    pdf.chapter_body(text)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        return tmp_file.name

# ✅ API Endpoint: Generate Resume
@app.post("/generate_resume/")
async def create_resume(
    file: UploadFile = File(...),
    applicant_details: str = Form(...),
    applicant_email: str = Form(...)
):
    """Extracts job description from file, generates resume, and returns a PDF."""
    try:
        content = await file.read()
        filename = file.filename.lower()

        # Extract job description from uploaded file
        if filename.endswith(".pdf"):
            from PyPDF2 import PdfReader
            job_description = "".join([page.extract_text() for page in PdfReader(io.BytesIO(content)).pages])
        elif filename.endswith(".docx"):
            import docx
            doc = docx.Document(io.BytesIO(content))
            job_description = "\n".join([para.text for para in doc.paragraphs])
        elif filename.endswith(".txt"):
            job_description = content.decode("utf-8")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading uploaded file: {str(e)}")

    # Generate the resume using the Assistant
    resume_text = await generate_resume(job_description, applicant_details)

    # Save generated resume as a PDF
    pdf_path = await save_pdf(resume_text)

    return FileResponse(pdf_path, media_type="application/pdf", filename="resume.pdf")

# ✅ API Root
@app.get("/")
async def root():
    return JSONResponse({"message": "Resume AI Service is running!"})
