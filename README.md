# Resops
This simple resume optimizer (**Resops**) extracts keywords from a job description and then checks to see if
the provided resume includes those keywords. The API is hosted on heroku and can be accessed by sending a POST
request including a body with the target resume and job description (see example below). The Yake and Spacy packages
are used for keyword searching and matching.  
You can also make use of the **hmm_app_name_tbd**, which uses the resops package (insert_link_here). This will 
allow you to enter a job description and your resume, and then provide you with feedback/allow you to edit 
your resume directly through the app.

## Project hosting links
- API: https://dashboard.heroku.com/apps/resume-optimizer
- hmm_app_name_tbd: insert_link_here

## How it works
- include a diagram or something to explain your confusing code
- yake used for keyword extract (also took the stopwords and used in inputs)
- in addition to keywords gotten from yake also takes top programming languages from "https://pypl.github.io/PYPL.html"

## Sample Code
### Python (API)
- write example

### Python (integration)
- write example

## Installing 
- dependencies: need a pip freeze in this b
- install instructions
- fastapi instructions
- sample call endpoint with requests

## TODO
- add examples to readme
- load models on startup (in main.py) to decrease time
- improve full-text resume parser
- tests??
- refactor to have "job_description" class in models

## citations
- **Yet Another Keyword Extractor (Yake)**  
In-depth journal paper at Information Sciences Journal: Campos, R., Mangaravite, V., Pasquali, A., Jatowt, A., Jorge, A., Nunes, C. and Jatowt, A. (2020). YAKE! Keyword Extraction from Single Documents using Multiple Local Features. In Information Sciences Journal. Elsevier, Vol 509, pp 257-289. https://doi.org/10.1016/j.ins.2019.09.013   
- **spaCy: Industrial-strength NLP**  
https://github.com/explosion/spaCy