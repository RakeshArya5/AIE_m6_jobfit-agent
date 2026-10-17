# JobFit Agent

JobFit Agent helps a job seeker apply for a job. You give it a job (a link, or the job description pasted as text) and your resume as a PDF. The agent reads both, compares the must-have skills of the job with the skills in your resume, gives you a match score and a list of missing skills, writes a short tailored cover letter, and saves the job to a tracker file (`tracker.json`). It is a hand-built agent loop using the OpenAI Chat Completions API, with a FastAPI back end and a Streamlit front end.

## Set up

1. Create and turn on a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate        (Windows)
   source .venv/bin/activate     (Mac / Linux)
   ```
2. Install the libraries:
   ```
   pip install -r requirements.txt
   ```
3. Create a file named `.env` in this folder with your OpenAI key:
   ```
   OPENAI_API_KEY=your-key-here
   ```

## Run

Open two terminals in this folder (with the virtual environment turned on).

Terminal 1, the back end:
```
uvicorn api:app --reload
```

Terminal 2, the front end:
```
streamlit run app.py
```

To test the back end on its own, open the test page: http://127.0.0.1:8000/docs

To test only the agent in the terminal: `python agent.py`
