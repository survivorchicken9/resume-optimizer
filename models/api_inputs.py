from typing import Union, TypeVar
from pydantic import BaseModel, StrictStr

D = TypeVar("D")  # docx file


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


# body for generate_cover_letter
class RawCoverLetter(BaseModel):
    cover_letter_docx: D
    first_name: StrictStr
    last_name: StrictStr
    job_title: StrictStr
    job_company: StrictStr
