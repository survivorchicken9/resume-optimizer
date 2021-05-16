from dataclasses import dataclass, field
from common.utils import load_programming_languages, load_stopwords, load_design_tools
from acora import AcoraBuilder


@dataclass
class JobDescription:
    job_title: str
    job_description: str
    job_company: str
    job_yake_keywords: list = field(default=None)
    job_skills: dict = field(default=None)
    job_keywords: list = field(default=None)

    def extract_job_description_yake_keywords(self, yake_extractor) -> list:
        stopwords = load_stopwords()

        # getting keywords using yake extractor
        raw_yake_output = yake_extractor.extract_keywords(self.job_description)
        yake_keywords = [
            keyword_tuple[0] for keyword_tuple in raw_yake_output
        ]  # not including score in tuple

        # removing duplicates, stopwords, and target company name (if exists)
        punctuation_chars = "!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~\\"
        all_keywords = [m for m in yake_keywords if m not in stopwords and m[0] not in punctuation_chars]
        try:
            all_keywords.remove(self.job_company)
        except ValueError:
            pass

        # adding found keywords to class instance
        self.job_yake_keywords = all_keywords

        return self.job_yake_keywords

    def extract_job_description_skills(self):
        # loading skill keywords from txt files
        skills_base_dict = {
            "programming_languages": load_programming_languages(),
            "design_tools": load_design_tools()
        }
        
        # finding other keywords from job field skill txt inputs
        found_skills_dict = dict()
        found_skills_list = list()  # easy to add to yake keywords in final function
        for skill_type, skill_list in skills_base_dict.items():
            acora_search_engine = AcoraBuilder(skill_list).build()
            found_skills_dict[skill_type] = [k[0] for k in acora_search_engine.findall(self.job_description)]
            found_skills_list += found_skills_dict[skill_type]
        self.job_skills = found_skills_dict
        return found_skills_list
        
    def extract_job_description_keywords(self, yake_extractor):
        yake_keywords = self.extract_job_description_yake_keywords(yake_extractor)
        skills_keywords = self.extract_job_description_skills()
        self.job_keywords = yake_keywords + skills_keywords
        return self.job_keywords, self.job_skills
