from fastapi import FastAPI
from models.resume import Resume
from typing import Union
from pydantic import BaseModel

app = FastAPI()


# body for get_resume_feedback
class RawResume(BaseModel):
	job_title: str
	job_description: str
	job_company: str
	raw_resume: Union[str, list]


@app.post("/")
def get_resume_feedback(raw_resume: RawResume) -> dict:
	"""
	Instantiates new resume, searches for keywords in job_description with Yake, compare resume and job description
	with spacy, return keywords found, missing keywords, and resume line by line feedback.
	:param raw_resume: json with job_title, job_description, job_company, and raw_resume
	:return: dict of results (check resume_lines_feedback for line by line feedback)
	"""
	resume = Resume(
		job_title=raw_resume.job_title,
		job_description=raw_resume.job_description,
		job_company=raw_resume.job_company,
		raw_resume=raw_resume.raw_resume
	)
	all_keywords = resume.extract_all_job_keywords()
	included_keywords, missing_keywords = resume.extract_included_and_missing_keywords()
	
	resume_lines_feedback = resume.get_resume_feedback()
	
	# combine results into one dict
	resume_feedback = {
		"job_title": raw_resume.job_title,
		"all_keywords": all_keywords,
		"included_keywords": included_keywords,
		"missing_keywords": missing_keywords,
		"resume_lines_feedback": resume_lines_feedback
	}
	
	return resume_feedback
