FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app/src

COPY poetry.lock pyproject.toml ./

RUN pip install poetry==2.2.0 && poetry install --no-root --without dev

COPY . .

CMD ["poetry", "run", "uvicorn", "app.service:app", "--host", "0.0.0.0", "--port", "8000"]
