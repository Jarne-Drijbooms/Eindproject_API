import json
import requests


def test_get_items():
    response = requests.get('http://127.0.0.1:8000/items/1')
    assert response.status_code == 200
    response_dictionary = json.loads(response.text)
    assert type(response_dictionary["race_won"]) == int
    assert type(response_dictionary["team"]) == str
    assert type(response_dictionary["name"]) == str


def test_get_error():
    response = requests.get('http://127.0.0.1:8000/users/me')
    assert response.status_code == 401



