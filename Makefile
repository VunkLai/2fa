pipeline: format lint test

format:
	black server --check --diff
	isort server --check-only --diff

lint:
	pylint server/*
	mypy server/

test:
	poetry run python server/manage.py check

requirements:
	poetry export -f requirements.txt --output requirements.txt

dev:
	poetry run python server/manage.py migrate
	poetry run python server/manage.py runserver

build: requirements
	rm -f server/db.sqlit3
	docker build -t two-factor-auth .

run:
	docker run --rm -d --network devops --name two-factor-auth

stop:
	docker stoptwo-factor-auth
