from typing import Union
from pydantic import BaseModel, StrictStr


# body for get_resume_feedback
class RawResume(BaseModel):
	job_title: StrictStr
	job_description: StrictStr
	job_company: StrictStr
	raw_resume: Union[StrictStr, list]


# body for get_highlighted_job_description
class HighlightInput(BaseModel):
	job_description: StrictStr
	job_keywords: list
