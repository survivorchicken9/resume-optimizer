from fastapi import FastAPI
from models.resume import Resume
from typing import Union
from pydantic import BaseModel

app = FastAPI()


class RawResume(BaseModel):
	job_title: str
	job_description: str
	job_company: str
	raw_resume: Union[str, list]


@app.post("/")
def get_resume_feedback(raw_resume: RawResume) -> dict:
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
