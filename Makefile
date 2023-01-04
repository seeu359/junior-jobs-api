run:
	uvicorn api.main:app --reload

lint:
	poetry run flake8

test:
	poetry run pytest tests

testlogic:
	poetry run pytest -v tests/test_logic.py

testroutes:
	poetry run pytest -v tests/test_routes.py

test-coverage:
	poetry run pytest --cov=jun_jobs_bot tests/ --cov-report xml

p_install:
	poetry install

install:
	pip install -r requirements.txt