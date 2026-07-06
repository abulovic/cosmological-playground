PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: check status next api-test

check:
	$(PYTHON) scripts/project.py validate
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v
	$(PYTHON) -m unittest discover -s services/api/tests -p 'test_*.py' -v

status:
	python3 scripts/project.py status --write

next:
	python3 scripts/project.py next

api-test:
	$(PYTHON) -m unittest discover -s services/api/tests -p 'test_*.py' -v
