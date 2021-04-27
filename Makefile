PYTHON = python3

.PHONY = test


test:
	pip install -e .
	pytest --cov --cov-report term-missing $(test_path)
