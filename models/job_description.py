from dataclasses import dataclass, field


@dataclass
class JobDescription:
	job_title: str
	job_description: str
	job_company: str
