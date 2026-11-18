.PHONY: install backend frontend test build

install:
	python3 -m venv backend/.venv
	backend/.venv/bin/python -m pip install -r backend/requirements.txt
	npm --prefix frontend ci

backend:
	cd backend && .venv/bin/python -m uvicorn app.main:app --reload

frontend:
	npm --prefix frontend run dev

test:
	cd backend && .venv/bin/python -m pytest -q

build:
	npm --prefix frontend run build
