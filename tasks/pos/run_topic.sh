### run in a virtual environment
uv venv .venv
### install requirements
uv pip install -r requirements.txt
### run
uv run --with-requirements requirements.txt python find_topic.py
