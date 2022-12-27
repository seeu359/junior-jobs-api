import pytest

from pydantic import ValidationError

from api.base_models import RequestParams, Response404
from api.exceptions import InvalidDateParams
from api.logic import process_user_request
from api.services import make_request_params


@pytest.mark.parametrize('language, compare_type',
                         [
                             ('python', 'today'),
                             ('java', 'today'),
                             ('ruby', 'today'),
                             ('python', 'week'),
                             ('java', 'week'),
                             ('php', 'month'),
                             ('ruby', 'month'),
                             ('ruby', 'month'),
                             ('python', 'custom'),
                             ('javascript', 'custom'),
                         ]
                         )
def test_process_valid_params(language, compare_type, correct_queries):
    date1, date2 = correct_queries
    model = process_user_request(language, compare_type, date1=date1, date2=date2)
    assert isinstance(model, RequestParams)


@pytest.mark.parametrize('language, compare_type',
                         [
                             ('python', 'today'),
                             ('java', 'today'),
                             ('javacript', 'month'),
                             ('javacript', 'month'),
                             ('php', 'custom'),
                             ('ruby', 'custom'),
                         ]
                         )
def test_process_not_valid_queries(language, compare_type, not_correct_queries):
    date1, date2 = not_correct_queries
    error = process_user_request(
        language, compare_type, date1=date1, date2=date2)
    assert isinstance(error, Response404)


@pytest.mark.parametrize('language, compare_type',
                         [
                             ('python', 'oday'),
                             ('jav', 'today'),
                             ('javacrit', 'month'),
                             ('java', 'mnth'),
                             ('php', 'custm'),
                             ('rby', 'custom'),
                             ('ph', 'week'),
                             ('java', 'wek'),

                         ]
                         )
def test_process_not_valid_path(language, compare_type):
    error = process_user_request(language, compare_type)
    assert isinstance(error, Response404)


@pytest.mark.parametrize('language, compare_type',
                         [
                             ('python', 'oday'),
                             ('jav', 'today'),
                             ('javacrit', 'month'),
                             ('java', 'mnth'),
                             ('php', 'custm'),
                             ('rby', 'custom'),
                             ('ph', 'week'),
                             ('java', 'wek'),
                             ('java', 'cutom'),

                         ]
                         )
def test_raise_errors(language, compare_type):
    with pytest.raises(ValidationError):
        make_request_params(language, compare_type=compare_type)
