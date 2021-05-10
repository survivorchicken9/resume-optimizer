from dataclasses import dataclass, field
from common.utils import load_programming_languages, load_stopwords
import re


@dataclass
class JobDescription:
	job_title: str
	job_description: str
	job_company: str
	job_keywords: list = field(default=None)

	def extract_job_description_keywords(self, yake_extractor) -> list:
		# get skills and stopwords from txt files
		programming_languages = load_programming_languages()
		stopwords = load_stopwords()
		
		# getting keywords using yake extractor
		raw_yake_output = yake_extractor.extract_keywords(self.job_description)
		yake_keywords = [keyword_tuple[0] for keyword_tuple in raw_yake_output]  # not including score in tuple
		
		# finding programming languages
		raw_list = re.sub(r'[.!,;?()]', ' ', self.job_description).split()  # remove punct and convert to list
		processed_list = list(set([j for j in raw_list if j.lower() in [k.lower() for k in programming_languages]]))
		
		# removing duplicates, stopwords, and target company name (if exists)
		all_keywords = list(set(yake_keywords + processed_list))
		all_keywords = [m for m in all_keywords if m not in stopwords]
		try:
			all_keywords.remove(self.job_company)
		except ValueError:
			pass
		
		# adding found keywords to class instance
		self.job_keywords = all_keywords
		
		return self.job_keywords
