SHELL := /bin/bash
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

venv:
	python -m venv $(VENV)

install: venv
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

test:
	$(PY) -m pytest -q

smoke:
	$(PY) scripts/smoke_run.py

notebook:
	$(PY) -m nbconvert --to notebook --execute tds_session_clustering_mercor_v2.ipynb --output artifacts/executed_notebook.ipynb
