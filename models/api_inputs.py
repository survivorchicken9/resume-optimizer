from typing import Union
from pydantic import BaseModel


# body for get_resume_feedback
class RawResume(BaseModel):
	job_title: str
	job_description: str
	job_company: str
	raw_resume: Union[str, list]


# body for get_highlighted_job_description
class HighlightInput(BaseModel):
	job_description: str
	job_keywords: list
