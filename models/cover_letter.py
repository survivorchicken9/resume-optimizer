from dataclasses import dataclass, field
from docxtpl import DocxTemplate
from typing import TypeVar
from os import remove

D = TypeVar("D")  # docx file


@dataclass
class CoverLetter:
    raw_cover_letter: D
    first_name: str
    last_name: str
    job_title: str
    job_company: str
    cover_letter_filename: str = field(default=None)

    def create_cover_letter_inputs(self) -> dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "job_title": self.job_title,
            "job_company": self.job_company,
        }

    def generate_cover_letter(self):
        cover_letter_inputs = self.create_cover_letter_inputs()
        cover_letter_doc = DocxTemplate(self.raw_cover_letter)
        cover_letter_doc.render(
            cover_letter_inputs
        )  # fill template jinja variables with input dict

        self.cover_letter_filename = (
            f"{self.first_name}_{self.last_name}_{self.job_company}_Cover_Letter.docx"
        )
        cover_letter_doc.save(self.cover_letter_filename)

        return self.cover_letter_filename

    def delete_cover_letter(self):
        if self.cover_letter_filename.endswith(".docx"):
            remove(self.cover_letter_filename)
        else:
            return f"File name does not end with docx: {self.cover_letter_filename}"
