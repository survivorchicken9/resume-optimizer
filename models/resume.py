import os
from dataclasses import dataclass, field
import uuid

import en_core_web_sm
import yake
from yake.highlight import TextHighlighter
import re
import spacy
from spacy.matcher import Matcher
from find_job_titles import FinderAcora
from typing import Union


@dataclass
class Resume:
	job_title: str
	job_description: str
	job_company: str
	raw_resume: Union[str, list] = field(default=None)
	included_keywords: list = field(default=None)
	missing_keywords: list = field(default=None)
	experience_metadata: dict = field(default_factory=lambda: dict())
	job_keywords: list = field(default=None)
	final_resume: str = field(default=None)
	_id: str = field(default_factory=lambda: uuid.uuid4().hex)
	
	@staticmethod
	def load_yake_extractor(
			language="en",
			max_ngram_size=3,
			deduplication_threshold=0.9,
			deduplication_algo="seqm",
			num_keywords=20
	) -> yake.KeywordExtractor:
		# hardcode parameters into yake extractor (change if needed later)
		return yake.KeywordExtractor(
			lan=language,
			n=max_ngram_size,
			dedupLim=deduplication_threshold,
			dedupFunc=deduplication_algo,
			top=num_keywords,
			features=None
		)
	
	@staticmethod
	def _load_programming_languages():
		with open(os.path.join("model_inputs", "programming_languages.txt"), "r") as f:
			programming_languages = f.read().splitlines()
		return programming_languages
	
	@staticmethod
	def _load_stopwords():
		with open(os.path.join("model_inputs", "stopwords.txt"), "r") as g:
			stopwords = g.read().splitlines()
		return stopwords
	
	def extract_all_job_keywords(self) -> list:
		# get skills and stopwords from txt files
		programming_languages = Resume._load_programming_languages()
		stopwords = Resume._load_stopwords()
		
		# getting keywords using yake extractor
		yake_extractor = Resume.load_yake_extractor()
		yake_keywords = [i[0] for i in yake_extractor.extract_keywords(self.job_description)]  # not including score
		
		# finding programming languages
		raw_list = re.sub(r'[.!,;?()]', ' ', self.job_description).split()
		processed_list = list(set([j for j in raw_list if j.lower() in [k.lower() for k in programming_languages]]))
		
		# removing duplicates, stopwords, and target company name
		all_keywords = list(set(yake_keywords + processed_list))
		all_keywords = [m for m in all_keywords if m not in stopwords]
		try:
			all_keywords.remove(self.job_company)
		except ValueError:
			pass
		
		# adding found keywords to class instance
		self.job_keywords = all_keywords
		
		return self.job_keywords
	
	# not necessary for frontend
	def get_highlighted_keywords_in_job_description(self):
		# using yake custom highlighter to return job_description with highlighted keywords
		custom_highlighter = TextHighlighter(max_ngram_size=3, highlight_pre="<b>", highlight_post="</b>")
		highlighted_description = custom_highlighter.highlight(self.job_description, self.job_keywords)
		
		# converting string to list and only including sentences with keywords
		description_sentences = highlighted_description.split(".")
		sentences_with_keywords = [s for s in description_sentences if "<b>" in s]
		
		return sentences_with_keywords
	
	def extract_included_and_missing_keywords(self):
		# can prob put this in a separate function maybe later idk
		nlp = en_core_web_sm.load()
		# nlp = spacy.load("en_core_web_sm")
		matcher = Matcher(nlp.vocab)
		rules = [[{"TEXT": keyword}] for keyword in self.job_keywords]
		matcher.add("keyword_matcher", rules)
		
		# configuring either str or list input into nlp doc and using in spacy matcher object
		resume_str = self.raw_resume
		if type(self.raw_resume) is list:
			resume_str = " ".join([experience["description"] for experience in self.raw_resume])
		raw_resume_doc = nlp(resume_str)
		raw_phrase_matches = matcher(raw_resume_doc)
		
		# adding all matched texts to results list
		phrase_matches_list = []
		for match_id, start, end in raw_phrase_matches:
			span = raw_resume_doc[start:end]  # the matched span
			phrase_matches_list.append(span.text)
		
		# removing duplicates from matched (included) keywords and assigning included/missing keyword lists
		self.included_keywords = list(set([k for k in phrase_matches_list if k in self.job_keywords]))
		self.missing_keywords = [n for n in self.job_keywords if n not in self.included_keywords]
		
		return self.included_keywords, self.missing_keywords
	
	def _convert_resume_str_to_dict(self):
		# job titles finder object tp get all job titles from resume using find_job_titles lib
		# this is the crappy one but we leave it in because i am lazy and this is the option i would use
		# even if it's not perfect
		finder = FinderAcora()
		job_titles = [title[2] for title in finder.findall(self.raw_resume)]
		job_titles_count = 0  # counter for adding job_title to experience_metadata later
		
		# init metadata dict and enumerate so we get the index of each line
		experience_metadata = dict()
		resume_lines_enumerated = enumerate(
			[line for line in self.raw_resume.split("\n") if line != ""])  # remove empty lines
		resume_lines_list = list(resume_lines_enumerated)
		
		# loop through lines to find job titles and experience (simple based on looking for bullet point in line)
		found_experience_name = None
		for resume_line in resume_lines_list:
			previous_line = resume_lines_list[int(resume_line[0]) - 1]  # using enumerate index in tuple(0)
			if "•" in resume_line[1]:  # check if this line is an "experience" line
				if "•" not in previous_line[1]:  # check if previous line is not an "experience" line (i.e. it is title)
					found_experience_name = job_titles[job_titles_count]
					job_titles_count += 1
				# found_experience_name = previous_line[1]  # rudimentary take previous line as title
				if found_experience_name not in experience_metadata.keys():
					experience_metadata[found_experience_name] = []  # init empty list for new experience
				experience_metadata[found_experience_name].append(resume_line[1])
		
		# only taking items with more than one line in description (heuristics to decrease items found)
		# this should look something like this (necessary input for the generating feedback)
		# experience_metadata = {"Job Title": ["In this job I did something", "I also did other things"], ...}
		self.experience_metadata = {key: value for (key, value) in experience_metadata.items() if len(value) > 1}

	def _convert_resume_list_to_dict(self):
		# this is how we're actually converting the frontend input
		# TODO need to ask nicole how to split the str
		# also this warning makes sense since technically this could be a string and not a list
		# BUT we take care of checking that in _convert_resume_raw_to_dict
		for experience in self.raw_resume:
			self.experience_metadata[experience["title"]] = [line for line in experience["description"].split("\n")]
	
	def _convert_resume_raw_to_dict(self) -> dict:
		# converting frontend input to fit get_resume_feedback necessary input format
		if type(self.raw_resume) is str:
			self._convert_resume_str_to_dict()
		else:
			self._convert_resume_list_to_dict()
		
		return self.experience_metadata
	
	def get_resume_feedback(self) -> list:
		# convert raw resume input to dict for processing
		self._convert_resume_raw_to_dict()
		
		# init results list and loop through parsed resume dict
		resume_feedback = []
		for job_title, experience_lines_list in self.experience_metadata.items():
			# check if line in each job has keyword and add to appropriate list
			lines_with_keywords = []
			lines_without_keywords = []
			for experience_line in experience_lines_list:
				if not any(word in experience_line for word in self.included_keywords):
					lines_without_keywords.append(experience_line)
					continue
				lines_with_keywords.append(experience_line)
			# add found job experience keywords match items as dict to results list
			resume_feedback.append(
				{
					"job_title": job_title,
					"lines_with_keyword": lines_with_keywords,
					"lines_without_keyword": lines_without_keywords
				}
			)
		
		return resume_feedback
	
	def generate_suggestions_from_keywords(self):
		# textgenrnn
		# https://github.com/minimaxir/textgenrnn/blob/master/docs/textgenrnn-demo.ipynb
		
		# Interactive textgenrnn Demo w/ GPU
		# https://colab.research.google.com/drive/1_3eG2EuyCUnyyuAU8_Ch05OOf14fOu5c?authuser=1#scrollTo=ClJwpF_ACONp
		
		# good looking dataset kaggle
		# https://www.kaggle.com/promptcloud/us-resumes-on-indeed-feb-2019
		pass
	
	def generate_preliminary_resume(self):
		pass
	
	def generate_final_resume(self):
		pass