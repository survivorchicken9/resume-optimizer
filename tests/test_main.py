from fastapi.testclient import TestClient
from main import app
from tests.test_main_inputs import data_list_test, data_str_test


client = TestClient(app)


def test_home():
	response = client.get("/")
	assert response.status_code == 200
	assert response.json() == {
		"msg": "hello there check out the docs if you're lost just add /docs to your current URL"
	}


def test_get_resume_feedback_list_input():
	response = client.post("/get_resume_feedback", json=data_list_test)
	result = response.json()
	assert response.status_code == 200
	assert isinstance(result, dict)
	assert len(result["all_keywords"]) > 0
	
	
def test_get_resume_feedback_str_input():
	response = client.post("/get_resume_feedback", json=data_str_test)
	result = response.json()
	assert response.status_code == 200
	assert isinstance(result, dict)
	assert len(result["all_keywords"]) > 0


def test_get_highlighted_job_description():
	pass
