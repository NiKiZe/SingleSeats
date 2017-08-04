pip install pytest-cov

PYTHONPATH=.
pip install pytest-pythonpath

py.test

py.test --cov= \
--cov-report=xml

test/ test_*.py (no __init__.py)