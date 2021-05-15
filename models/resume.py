from dataclasses import dataclass, field
import uuid
import yake
from yake.highlight import TextHighlighter
from find_job_titles import FinderAcora
from models.job_description import JobDescription
from typing import Union, Tuple


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
    job_skills: dict = field(default=None)
    final_resume: str = field(default=None)
    _id: str = field(default_factory=lambda: uuid.uuid4().hex)

    @staticmethod
    def load_yake_extractor(
        language="en",
        max_ngram_size=3,
        deduplication_threshold=0.9,
        deduplication_algo="seqm",
        num_keywords=20,
    ) -> yake.KeywordExtractor:
        # hardcode parameters into yake extractor (change if needed later)
        return yake.KeywordExtractor(
            lan=language,
            n=max_ngram_size,
            dedupLim=deduplication_threshold,
            dedupFunc=deduplication_algo,
            top=num_keywords,
            features=None,
        )

    # instantiating new job_description object and running extract methods
    def extract_all_job_keywords(self, yake_extractor) -> Tuple[list, dict]:
        job_description = JobDescription(
            job_title=self.job_title,
            job_description=self.job_description,
            job_company=self.job_company,
        )

        self.job_keywords, self.job_skills = job_description.extract_job_description_keywords(yake_extractor)

        return self.job_keywords, self.job_skills

    # not used in frontend
    @staticmethod
    def get_highlighted_keywords_in_job_description(
        job_description: str, job_keywords: list, highlight_tag: str = "b"
    ):
        max_ngram_keyword_len = int(
            max([len(keyword.split()) for keyword in job_keywords])
        )

        # using yake custom highlighter to return job_description with highlighted keywords
        custom_highlighter = TextHighlighter(
            max_ngram_size=max_ngram_keyword_len,
            highlight_pre=f"<{highlight_tag}>",
            highlight_post=f"</{highlight_tag}>",
        )
        highlighted_description = custom_highlighter.highlight(
            job_description, job_keywords
        )

        # maybe use this in another function
        # # converting string to list and only including sentences with keywords
        # description_sentences = highlighted_description.split(".")
        # sentences_with_keywords = [s for s in description_sentences if "<b>" in s]

        return highlighted_description

    def extract_included_and_missing_keywords(self, matcher, spacy_model):
        # add keywords to spacy matcher
        rules = [[{"TEXT": keyword}] for keyword in self.job_keywords]
        matcher.add("keyword_matcher", rules)

        # configuring either str or list input into nlp doc and using in spacy matcher object
        resume_str = self.raw_resume
        if type(self.raw_resume) is list:
            resume_str = " ".join(
                [experience["description"] for experience in self.raw_resume]
            )
        raw_resume_doc = spacy_model(resume_str)
        raw_phrase_matches = matcher(raw_resume_doc)

        # adding all matched texts to results list
        phrase_matches_list = []
        for match_id, start, end in raw_phrase_matches:
            span = raw_resume_doc[start:end]  # the matched span
            phrase_matches_list.append(span.text)

        # removing duplicates from matched (included) keywords and assigning included/missing keyword lists
        self.included_keywords = list(
            set([k for k in phrase_matches_list if k in self.job_keywords])
        )
        self.missing_keywords = [
            n for n in self.job_keywords if n not in self.included_keywords
        ]

        return self.included_keywords, self.missing_keywords

    def _convert_resume_str_to_dict(self):
        # job titles finder object tp get all job titles from resume using find_job_titles lib
        # this is the crappy one but we leave it in because i am lazy and this is the option i would use
        # even if it's not perfect
        finder = FinderAcora()
        job_titles = [title[2] for title in finder.findall(self.raw_resume)]
        job_titles_count = (
            0  # counter for adding job_title to experience_metadata later
        )

        # init metadata dict and enumerate so we get the index of each line
        experience_metadata = dict()
        resume_lines_enumerated = enumerate(
            [line for line in self.raw_resume.split("\n") if line != ""]
        )  # remove empty lines
        resume_lines_list = list(resume_lines_enumerated)

        # loop through lines to find job titles and experience (simple based on looking for bullet point in line)
        found_experience_name = None
        for resume_line in resume_lines_list:
            previous_line = resume_lines_list[
                int(resume_line[0]) - 1
            ]  # using enumerate index in tuple(0)
            if "•" in resume_line[1]:  # check if this line is an "experience" line
                if (
                    "•" not in previous_line[1]
                ):  # check if previous line is not an "experience" line (i.e. it is title)
                    found_experience_name = job_titles[job_titles_count]
                    job_titles_count += 1
                # found_experience_name = previous_line[1]  # rudimentary take previous line as title
                if found_experience_name not in experience_metadata.keys():
                    experience_metadata[
                        found_experience_name
                    ] = []  # init empty list for new experience
                experience_metadata[found_experience_name].append(resume_line[1])

        # only taking items with more than one line in description (heuristics to decrease items found)
        # this should look something like this (necessary input for the generating feedback)
        # experience_metadata = {"Job Title": ["In this job I did something", "I also did other things"], ...}
        self.experience_metadata = {
            key: value for (key, value) in experience_metadata.items() if len(value) > 1
        }

    def _convert_resume_list_to_dict(self):
        # this is how we're actually converting the frontend input
        # TODO need to ask nicole how to split the str
        # also this warning makes sense since technically this could be a string and not a list
        # BUT we take care of checking that in _convert_resume_raw_to_dict
        for experience in self.raw_resume:
            self.experience_metadata[experience["title"]] = [
                line for line in experience["description"].split("\n")
            ]

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
                    "lines_without_keyword": lines_without_keywords,
                }
            )

        return resume_feedback
    
    def get_resume_keyword_score(self) -> str:
        return f"{len(self.included_keywords)}/{len(self.job_keywords)}"

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
