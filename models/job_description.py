from dataclasses import dataclass, field
from common.utils import load_programming_languages, load_stopwords, load_design_tools
import re
from acora import AcoraBuilder


@dataclass
class JobDescription:
    job_title: str
    job_description: str
    job_company: str
    job_keywords: list = field(default=None)

    def extract_job_description_keywords(self, yake_extractor) -> list:
        # get skills and stopwords from txt files
        programming_languages = load_programming_languages()
        design_tools = load_design_tools()
        stopwords = load_stopwords()

        # getting keywords using yake extractor
        raw_yake_output = yake_extractor.extract_keywords(self.job_description)
        yake_keywords = [
            keyword_tuple[0] for keyword_tuple in raw_yake_output
        ]  # not including score in tuple

        # finding other keywords from job field skill txt inputs
        found_skills = list()
        for skill_keyword_list in [programming_languages, design_tools]:
            acora_search_engine = AcoraBuilder(skill_keyword_list).build()
            found_skills += [
                k[0] for k in acora_search_engine.findall(self.job_description)
            ]

        # removing duplicates, stopwords, and target company name (if exists)
        all_keywords = list(set(yake_keywords + found_skills))
        all_keywords = [m for m in all_keywords if m not in stopwords]
        try:
            all_keywords.remove(self.job_company)
        except ValueError:
            pass

        # adding found keywords to class instance
        self.job_keywords = all_keywords

        return self.job_keywords
