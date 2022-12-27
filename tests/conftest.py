import pytest


@pytest.fixture()
def queries_is_none():
    date1 = None
    date2 = None
    return date1, date2


@pytest.fixture()
def correct_queries():
    date1 = '2022-11-13'
    date2 = '2022-12-16'
    return date1, date2


@pytest.fixture()
def not_correct_queries():
    date1 = '2022-12-13'
    date2 = '2022-11-01'
    return date1, date2
