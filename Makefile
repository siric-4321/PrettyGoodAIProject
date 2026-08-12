.PHONY: test server one all

test:
	pytest -q

server:
	uvicorn app.server:app --host 0.0.0.0 --port 8000

one:
	python run.py --scenario 01_simple_schedule

all:
	python run.py --all
