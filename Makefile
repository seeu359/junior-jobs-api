run:
	uvicorn api.scripts.app:app --reload

lint:
	poetry run flake8
