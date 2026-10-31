.PHONY: install clean validate eda test run

install:
	pip install -r requirements.txt

clean:
	python -c "import shutil, os; [shutil.rmtree(p, ignore_errors=True) for p in ['__pycache__', '.pytest_cache', 'build', 'dist', 'src/aidy.egg-info']]"

validate:
	python scripts/validate_dataset.py

synthetic:
	python scripts/generate_synthetic_data.py

eda:
	python scripts/run_eda.py

test:
	pytest -v

run:
	streamlit run app.py
