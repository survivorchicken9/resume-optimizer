import en_core_web_sm
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from models.resume import Resume
from models.cover_letter import CoverLetter
from spacy.matcher import Matcher
from models.api_inputs import RawResume, HighlightInput, RawCoverLetter

# local run command:
# uvicorn main:app --reload

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
    all_keywords, all_skills = resume.extract_all_job_keywords(yake_extractor=yake_extractor)
    included_keywords, missing_keywords = resume.extract_included_and_missing_keywords(
        matcher=matcher, spacy_model=spacy_model
    )

    resume_lines_feedback = resume.get_resume_feedback()
    resume_keyword_score = resume.get_resume_keyword_score()
    
    # combine results into one dict
    resume_feedback = {
        "job_title": raw_resume.job_title,
        "all_keywords": all_keywords,
        "skills": all_skills,
        "included_keywords": included_keywords,
        "missing_keywords": missing_keywords,
        "keyword_score": resume_keyword_score,
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


# @app.post("/generate_cover_letter")
# def generate_cover_letter(raw_cover_letter: RawCoverLetter):
#     # TODO https://fastapi.tiangolo.com/tutorial/request-files/
#     cover_letter = CoverLetter(
#         input_cover_letter=raw_cover_letter.cover_letter_docx,
#         first_name=raw_cover_letter.first_name,
#         last_name=raw_cover_letter.last_name,
#         job_title=raw_cover_letter.job_title,
#         job_company=raw_cover_letter.job_company
#     )
#
#     # generate and return cover letter (and delete after returning)
#     cover_letter_file_name = cover_letter.generate_final_cover_letter()
#
#     return FileResponse(cover_letter_file_name)


@app.get("/")
def home():
    return {
        "msg": "hello there check out the docs if you're lost just add /docs to your current URL"
    }
