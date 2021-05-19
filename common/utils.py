import os


def load_programming_languages():
    with open(os.path.join("common", "keyword_inputs", "programming_languages.txt"), "r") as f:
        programming_languages = f.read().splitlines()
    return programming_languages


def load_design_tools():
    with open(os.path.join("common", "keyword_inputs", "design_tools.txt"), "r") as f:
        design_tools = f.read().splitlines()
    return design_tools


def load_business_analyst_skills():
    with open(os.path.join("common", "keyword_inputs", "business_analyst_skills.txt"), "r") as f:
        business_analyst_skills = f.read().splitlines()
    return business_analyst_skills


def load_stopwords():
    with open(os.path.join("common", "keyword_inputs", "stopwords.txt"), "r") as g:
        stopwords = g.read().splitlines()
    return stopwords
