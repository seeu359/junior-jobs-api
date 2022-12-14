import pytest
from api.scripts.app import app
from fastapi.testclient import TestClient


client = TestClient(app)


@pytest.mark.parametrize('path',
                         [
                             'python',
                             'java',
                             'ruby',
                             'php',
                             'javascript',
                         ])
def test_stat_language_route(path):
    response = client.get('/stat/' + path)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.parametrize('path',
                         [
                             'php/today',
                             'ruby/today',
                             'python/today',
                             'javascript/today',
                             'java/today',

                         ])
def test_compare_type_today_stat_route(path):
    response = client.get('/stat/' + path)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


@pytest.mark.parametrize('path',
                         [
                             'php/week',
                             'ruby/week',
                             'python/week',
                             'javascript/week',
                             'java/week',
                         ])
def test_compare_type_week_stat_route(path):
    response = client.get('/stat/' + path)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


@pytest.mark.parametrize('path',
                         [
                             'php/month',
                             'ruby/month',
                             'python/month',
                             'javascript/month',
                             'java/month',
                         ])
def test_compare_type_month_stat_route(path):
    response = client.get('/stat/' + path)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
