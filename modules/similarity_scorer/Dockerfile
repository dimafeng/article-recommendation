from intel/intel-optimized-pytorch:pip-ipex-1.13.100-ubuntu-22.04

# Set working directory
WORKDIR /app
COPY . /app

RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

CMD ["poetry", "run", "python", "/app/similarity_scorer/main.py"]