"""FastAPI back end for JobFit Agent."""

import os
from datetime import datetime

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from agent import JobFitResult, run_agent
from tools import load_tracker

# Folder where uploaded resumes are saved
UPLOAD_FOLDER = "uploads"

app = FastAPI(title="JobFit Agent API")


def save_upload(resume: UploadFile) -> str:
    """Save the uploaded PDF in uploads/ with a unique name and return its path."""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Unique name: date and time + the original file name
    time_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_name = os.path.basename(resume.filename)
    file_path = os.path.join(UPLOAD_FOLDER, f"{time_stamp}_{original_name}")

    with open(file_path, "wb") as file:
        file.write(resume.file.read())
    return file_path


@app.post("/jobfit", summary="Match a resume to a job and write a cover letter", response_model=JobFitResult)
async def jobfit(
    resume: UploadFile = File(..., description="The resume as a PDF file"),
    job_url: str = Form("", description="Link to the job post (optional)"),
    job_text: str = Form("", description="Job description pasted as text (optional)"),
):
    # Check that a job link or job text was given
    if job_url.strip() == "" and job_text.strip() == "":
        raise HTTPException(status_code=400, detail="Please give a job link or paste the job description text.")

    # Check that the file is a PDF
    if resume.filename is None or not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="The resume must be a PDF file.")

    # Save the PDF, then run the agent on it
    try:
        resume_path = save_upload(resume)
    except OSError:
        raise HTTPException(status_code=500, detail="Could not save the uploaded resume. Please try again.")
    return await run_agent(resume_path, job_url=job_url.strip(), job_text=job_text)


@app.get("/tracker", summary="List all saved job applications")
def tracker():
    return load_tracker()


@app.get("/health", summary="Check that the back end is running")
def health():
    return {"status": "ok"}
