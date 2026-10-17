"""Streamlit front end for JobFit Agent. It calls the FastAPI back end."""

import requests
import streamlit as st

# Address of the FastAPI back end
API_URL = "http://127.0.0.1:8000"

# Shown when the back end cannot be reached
BACKEND_DOWN_MESSAGE = "Start the back end first: uvicorn api:app --reload"


def error_text(response) -> str:
    """Get the error message from a back-end response."""
    try:
        return str(response.json()["detail"])
    except (ValueError, KeyError):
        return "Something went wrong in the back end. Please try again."


def call_jobfit(job_url: str, job_text: str, resume_file) -> dict:
    """Send the job and resume to POST /jobfit. Return the result or an error."""
    form_data = {"job_url": job_url, "job_text": job_text}
    files = {"resume": (resume_file.name, resume_file.getvalue(), "application/pdf")}
    try:
        response = requests.post(f"{API_URL}/jobfit", data=form_data, files=files, timeout=120)
    except requests.exceptions.ConnectionError:
        return {"error": BACKEND_DOWN_MESSAGE}
    except requests.exceptions.Timeout:
        return {"error": "The agent took too long to answer. Please try again."}

    if response.status_code != 200:
        return {"error": error_text(response)}
    return response.json()


def show_skill_list(title: str, skills: list[str]) -> None:
    """Show a heading and a bullet list of skills."""
    st.subheader(title)
    if len(skills) == 0:
        st.write("None")
    for skill in skills:
        st.markdown(f"- {skill}")


def show_result(result: dict) -> None:
    """Show the agent's result on the page."""
    # Errors from the back end or the connection
    if "error" in result:
        st.error(result["error"])
        return

    # The agent could not finish, for example the link was blocked
    if result["status"] != "ok":
        st.warning(result["message"])
        return

    # Match score, then matched and missing skills side by side
    st.metric("Match score", f"{result['match_score']}%")
    left_column, right_column = st.columns(2)
    with left_column:
        show_skill_list("Matched skills", result["matched_skills"])
    with right_column:
        show_skill_list("Missing skills", result["missing_skills"])

    # Cover letter in a text area so it is easy to copy
    st.subheader("Cover letter")
    st.text_area("Copy your cover letter", result["cover_letter"], height=300)
    st.info(result["message"])


def show_tracker() -> None:
    """Show the saved jobs from GET /tracker as a table."""
    st.header("My tracker")
    try:
        response = requests.get(f"{API_URL}/tracker", timeout=10)
    except requests.exceptions.RequestException:
        st.error(BACKEND_DOWN_MESSAGE)
        return

    rows = response.json()
    if len(rows) == 0:
        st.write("No saved jobs yet.")
    else:
        st.dataframe(rows)


# ----- Page -----
st.title("JobFit Agent")
st.write("Give a job and your resume. The agent scores your match, lists missing skills and writes a cover letter.")

# Inputs
job_url = st.text_input("Job link")
job_text = st.text_area("Or paste the job description text (use this if the link does not work)")
resume_file = st.file_uploader("Your resume (PDF)", type=["pdf"])

# Run the agent when the button is clicked
if st.button("Analyse"):
    if resume_file is None:
        st.warning("Please upload your resume as a PDF.")
    elif job_url.strip() == "" and job_text.strip() == "":
        st.warning("Please give a job link or paste the job description text.")
    else:
        with st.spinner("The agent is working..."):
            st.session_state["result"] = call_jobfit(job_url, job_text, resume_file)

# Keep showing the last result when the page reloads
if "result" in st.session_state:
    show_result(st.session_state["result"])

show_tracker()
