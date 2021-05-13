import en_core_web_sm
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from models.resume import Resume
from spacy.matcher import Matcher
from models.api_inputs import RawResume, HighlightInput

# local run command: uvicorn main:app --reload

# set up app and CORS middleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"]
)

# load yake extractor
yake_extractor = Resume.load_yake_extractor()

# load spacy matcher
spacy_model = en_core_web_sm.load()
matcher = Matcher(spacy_model.vocab)


@app.post("/get_resume_feedback")
def get_resume_feedback(raw_resume: RawResume) -> dict:
    """
    Instantiates new resume, searches for keywords in job_description with Yake,
    compare resume and job description with spacy, return keywords found, missing keywords,
    and resume line by line feedback.
    :param raw_resume: json with job_title, job_description, job_company, and raw_resume
    :return: dict of results (check resume_lines_feedback for line by line feedback)
    """
    resume = Resume(
        job_title=raw_resume.job_title,
        job_description=raw_resume.job_description,
        job_company=raw_resume.job_company,
        raw_resume=raw_resume.raw_resume,
    )
    all_keywords = resume.extract_all_job_keywords(yake_extractor=yake_extractor)
    included_keywords, missing_keywords = resume.extract_included_and_missing_keywords(
        matcher=matcher, spacy_model=spacy_model
    )

    resume_lines_feedback = resume.get_resume_feedback()

    # combine results into one dict
    resume_feedback = {
        "job_title": raw_resume.job_title,
        "all_keywords": all_keywords,
        "included_keywords": included_keywords,
        "missing_keywords": missing_keywords,
        "resume_lines_feedback": resume_lines_feedback,
    }

    return resume_feedback


@app.post("/highlighted_job_description")
def get_highlighted_job_description(highlight_input: HighlightInput):
    """
    Making use of the yake TextHighlighter feature to return a job description string that has keywords bolded
    :param highlight_input: job_description as a string and job_keywords as a list
    :return: job_description as a string with highlighted keywords in bold
    """
    highlighted_job_description = Resume.get_highlighted_keywords_in_job_description(
        job_description=highlight_input.job_description,
        job_keywords=highlight_input.job_keywords,
    )

    return highlighted_job_description


@app.get("/")
def main():
    return "hello there check out the docs if you're lost just add /docs to your current URL"


# @app.get("/generate_cover_letter")
# def generate_cover_letter():
# 	# return FileResponse("test.docx")
# 	# TODO use cover_letter model here
# 	return "wip"
