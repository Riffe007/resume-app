from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import openai
import os
import tempfile
import asyncio
import io
import json
import time
from dotenv import load_dotenv
from openai import AzureOpenAI
from PyPDF2 import PdfFileReader

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Azure OpenAI API Credentials
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")
ASSISTANT_ID = os.getenv("AZURE_ASSISTANT_ID")

# Ensure required credentials are set
if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY or not VECTOR_STORE_ID or not ASSISTANT_ID:
    raise ValueError("Missing required environment variables!")

# Initialize OpenAI Client
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2024-05-01-preview"
)

# Function to retrieve relevant experience from Vector Store
def retrieve_relevant_experience(job_description):
    try:
        search_results = client.beta.vector_stores.files.search(
            vector_store_id=VECTOR_STORE_ID,
            query=job_description,
            max_results=5
        )
        return "\n".join([doc["text"] for doc in search_results["data"]])
    except Exception as e:
        print(f"❌ Error retrieving experience: {str(e)}")
        return ""

# Function to interact with OpenAI Assistant
async def generate_resume(job_description: str, applicant_details: str) -> str:
    """Uses Azure OpenAI Assistant to generate a tailored resume."""
    try:
        retrieved_experience = retrieve_relevant_experience(job_description)

        # Create a new Thread for the conversation
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
            assistant_id=ASSISTANT_ID
        )

        # Loop until the run completes
        while run.status in ['queued', 'in_progress']:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        # Handle the response
        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            return messages[0]["content"]

        elif run.status == 'requires_action':
            print("⚠️ Assistant requires function execution.")
            return "Assistant requires additional processing."

        else:
            return f"❌ Assistant failed with status: {run.status}"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume generation failed: {str(e)}")
# Function to extract text from PDF
def extract_text_from_pdf(content):
    pdf_reader = PdfFileReader(io.BytesIO(content))
    text = ""
    for page_num in range(pdf_reader.getNumPages()):
        text += pdf_reader.getPage(page_num).extractText()
    return text

# Function to extract text from DOCX
def extract_text_from_docx(content):
    import docx
    doc = docx.Document(io.BytesIO(content))
    return "\n".join([para.text for para in doc.paragraphs])

# Function to extract text from TXT
def extract_text_from_txt(content):
    return content.decode("utf-8")

# API Endpoint to Generate Resume
# API Endpoint to Generate Resume
@app.post("/generate_resume/")
async def create_resume(
    file: UploadFile = File(...),
    applicant_details: str = Form(...),
    applicant_email: str = Form(...)
):
    """Extracts job description from file, generates resume, and returns PDF."""
    try:
        content = await file.read()
        filename = file.filename.lower()

        # Extract job description from uploaded file
        if filename.endswith(".pdf"):
            job_description = extract_text_from_pdf(content)
        elif filename.endswith(".docx"):
            job_description = extract_text_from_docx(content)
        elif filename.endswith(".txt"):
            job_description = extract_text_from_txt(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading uploaded file: {str(e)}")

    # Generate the resume using Assistant
    resume_text = await generate_resume(job_description, applicant_details)

    # Save generated resume as a PDF
    pdf_path = await save_pdf(resume_text)

    return FileResponse(pdf_path, media_type="application/pdf", filename="resume.pdf")

# Function to save text as PDF
async def save_pdf(text: str) -> str:
    from fpdf import FPDF

    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Generated Resume', 0, 1, 'C')

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

        def chapter_title(self, title):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, title, 0, 1, 'L')
            self.ln(10)

        def chapter_body(self, body):
            self.set_font('Arial', '', 12)
            self.multi_cell(0, 10, body)
            self.ln()

    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title("Resume")
    pdf.chapter_body(text)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        return tmp_file.name

# Root Endpoint
@app.get("/")
async def root():
    return JSONResponse({"message": "Resume AI Service is running!"})
