run:
	uv run fastapi dev --port 9000

run-qa:
	env=qa uv run fastapi dev --port 9000

run-prod:
	env=prod uv run fastapi dev --port 9000


	