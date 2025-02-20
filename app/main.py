from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import tempfile, asyncio, io
from fpdf import FPDF
from PyPDF2 import PdfReader
import docx

app = FastAPI()

async def generate_resume(job_description: str, applicant_details: str) -> str:
    """
    Simulate generating a tailored resume using the job description and applicant details.
    In production, replace this with a call to your fine-tuned model.
    """
    prompt = (
        f"Generate a tailored resume for the following applicant:\n"
        f"{applicant_details}\n\n"
        f"Based on this job description:\n{job_description}\n\n"
        f"Please format the resume with clear sections."
    )
    await asyncio.sleep(1)  # Simulate processing delay
    resume_text = (
        f"Tailored Resume\n\n"
        f"Applicant: {applicant_details}\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"[Generated Resume Content Based on Prompt: {prompt}]"
    )
    return resume_text

def generate_pdf(text: str, output_path: str):
    """
    Create a simple PDF from the resume text using FPDF.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.cell(0, 10, txt=line, ln=True)
    pdf.output(output_path)

async def send_to_hubspot(applicant_email: str, resume_status: str):
    """
    Simulate sending the resume status to HubSpot.
    Replace with actual API integration in production.
    """
    await asyncio.sleep(1)
    return {"status": "sent", "email": applicant_email, "resume_status": resume_status}

def extract_text_from_pdf(content: bytes) -> str:
    """
    Extract text from a PDF file using PyPDF2.
    """
    reader = PdfReader(io.BytesIO(content))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

def extract_text_from_docx(content: bytes) -> str:
    """
    Extract text from a Word document (.docx) using python-docx.
    """
    document = docx.Document(io.BytesIO(content))
    full_text = []
    for para in document.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def extract_text_from_txt(content: bytes) -> str:
    """
    Decode plain text content as UTF-8.
    """
    return content.decode("utf-8")

@app.post("/generate_resume")
async def create_resume(
    file: UploadFile = File(...),
    applicant_details: str = Form(...),
    applicant_email: str = Form(...)
):
    try:
        content = await file.read()
        lower_filename = file.filename.lower()
        if lower_filename.endswith(".pdf"):
            job_description = extract_text_from_pdf(content)
        elif lower_filename.endswith(".docx"):
            job_description = extract_text_from_docx(content)
        elif lower_filename.endswith(".txt"):
            job_description = extract_text_from_txt(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading uploaded file. Details: {str(e)}")

    resume_text = await generate_resume(job_description, applicant_details)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf_path = tmp_file.name
    generate_pdf(resume_text, pdf_path)

    # Optionally send a status update to HubSpot
    await send_to_hubspot(applicant_email, "Resume Generated")

    return FileResponse(pdf_path, media_type="application/pdf", filename="resume.pdf")

@app.get("/")
async def root():
    return JSONResponse({"message": "Resume AI Service is running"})
