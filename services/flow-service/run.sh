eval $(poetry env activate)
PYTHONPATH=src uvicorn app.service:app --reload --port 8000