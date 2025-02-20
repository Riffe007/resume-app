from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import os
import asyncio
from fpdf import FPDF

app = FastAPI()

# --- Helper Functions ---

async def generate_resume(job_description: str, applicant_details: str) -> str:
    """
    Simulate generating a tailored resume using the job description and applicant details.
    In a production setup, this function would call the Azure OpenAI GPT-4 API,
    possibly using a fine-tuned model (from your JSONL file) to generate the resume.
    """
    # Build a prompt that incorporates the job description and applicant details.
    prompt = (
        f"Generate a tailored resume for the following applicant:\n"
        f"{applicant_details}\n\n"
        f"Based on this job description:\n{job_description}\n\n"
        f"Please format the resume with clear sections."
    )
    
    # Simulate network/API delay
    await asyncio.sleep(1)
    
    # Dummy resume content. Replace this with the actual API call.
    resume_text = (
        f"Tailored Resume\n\n"
        f"Applicant: {applicant_details}\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"[Generated Resume Content Here based on prompt: {prompt}]"
    )
    return resume_text

def generate_pdf(text: str, output_path: str):
    """
    Generate a simple PDF file from text using FPDF.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.cell(0, 10, txt=line, ln=True)
    pdf.output(output_path)

async def send_to_hubspot(applicant_email: str, resume_status: str):
    """
    Simulate sending resume status to HubSpot.
    In production, use an HTTP client (like httpx or requests) to make API calls to HubSpot.
    """
    await asyncio.sleep(1)
    # Dummy response—replace with actual API integration
    return {"status": "sent", "email": applicant_email, "resume_status": resume_status}

# --- Endpoints ---

@app.post("/generate_resume")
async def create_resume(
    file: UploadFile = File(...),
    applicant_details: str = Form(...),
    applicant_email: str = Form(...)
):
    """
    Accepts a job description file upload along with applicant details and email.
    Uses the file content as a prompt to generate a tailored resume, converts it to a PDF,
    sends a resume status to HubSpot, and returns the PDF for download.
    """
    try:
        content = await file.read()
        job_description = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error reading uploaded file.")

    # Generate resume text using the uploaded job description and applicant details.
    resume_text = await generate_resume(job_description, applicant_details)

    # Generate a PDF from the resume text in a temporary file.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf_path = tmp_file.name
    generate_pdf(resume_text, pdf_path)

    # Optionally, send resume status to HubSpot asynchronously.
    hubspot_response = await send_to_hubspot(applicant_email, "Resume Generated")
    # (In a real implementation, you might log or use hubspot_response as needed.)

    # Return the PDF file as the response for download.
    return FileResponse(pdf_path, media_type="application/pdf", filename="resume.pdf")

@app.get("/")
async def root():
    """
    Simple health check endpoint.
    """
    return JSONResponse({"message": "Resume AI Service is running"})
