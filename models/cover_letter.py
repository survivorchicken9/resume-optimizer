from dataclasses import dataclass, field
from docxtpl import DocxTemplate
from typing import TypeVar
from os import remove
import time

D = TypeVar("D")  # docx file


@dataclass
class CoverLetter:
    input_cover_letter: D
    first_name: str
    last_name: str
    job_title: str
    job_company: str
    cover_letter_filename: str = field(default=None)

    def _create_cover_letter_inputs(self) -> dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "job_title": self.job_title,
            "job_company": self.job_company,
        }

    def _delete_cover_letter(self):
        if self.cover_letter_filename.endswith(".docx"):
            remove(self.cover_letter_filename)
        else:
            return f"File name does not end with docx: {self.cover_letter_filename}"

    def generate_final_cover_letter(self):
        # fill docx template jinja variables with input dict
        cover_letter_inputs = self._create_cover_letter_inputs()  # creating input dict for doc.render()
        cover_letter_doc = DocxTemplate(self.input_cover_letter)  # takes filepath
        cover_letter_doc.render(cover_letter_inputs)

        self.cover_letter_filename = f"{self.first_name}_{self.last_name}_{self.job_company}_Cover_Letter.docx"
        cover_letter_doc.save(self.cover_letter_filename)
        
        # TODO this doesn't work lol
        try:
            return self.cover_letter_filename
        finally:
            self._delete_cover_letter()
