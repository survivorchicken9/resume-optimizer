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

## Installing 
This project is keeping track of dependencies using pipenv. To install all required packages and the 
correct versions, simply create a virtual environment and run the following inside it:
```
pipenv install
```
  
To run the FastAPI server on your local machine and be able to call the endpoints in main.py locally, 
run the following:
```
uvicorn main:app --reload
```

## Sample Code
### Python (API)
First, define some sample inputs:
```python
data = {
    "job_title" : "Software Engineer",
    "job_description" : "Company A is looking for a Software Engineer to grow its...",
    "job_company" : "Company A",
    "raw_resume" : [{"title": "Software Engineer", "description": "Deployed machine learning models to production..."}]
}
```
Then, use the requests module to send a post request to the endpoint (locally or to the API):
```python
import requests
resume_feedback_local = requests.post("http://127.0.0.1:8000/get_resume_feedback", json=data).text
resume_feedback_api = requests.post("https://resume-optimizer.herokuapp.com/get_resume_feedback", json=data).text
```
You can visit the [API docs](https://resume-optimizer.herokuapp.com/docs) for more information.


### Python (integration)
- TODO write example

## TODO
- finish adding examples to readme
- improve full-text resume parser
- tests????
- improve job_description class keyword extraction methods
- include graphic design keyword match from txt

## Citations
- **Yet Another Keyword Extractor (Yake)**  
In-depth journal paper at Information Sciences Journal: Campos, R., Mangaravite, V., Pasquali, A., Jatowt, A., Jorge, A., Nunes, C. and Jatowt, A. (2020). YAKE! Keyword Extraction from Single Documents using Multiple Local Features. In Information Sciences Journal. Elsevier, Vol 509, pp 257-289. https://doi.org/10.1016/j.ins.2019.09.013   
- **spaCy: Industrial-strength NLP**  
https://github.com/explosion/spaCy