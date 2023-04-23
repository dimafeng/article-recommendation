# First stage: build the application
FROM python:3.10-slim AS builder

# Set working directory
WORKDIR /app

# Copy and install the dependencies
COPY poetry.lock pyproject.toml /app/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# Copy the application code
COPY . /app/

RUN poetry install

# Set the command to run the application
CMD ["poetry", "run", "python", "/app/article_recs/application.py"]
