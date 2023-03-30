from intel/intel-optimized-pytorch:1.12.100

RUN pip install --upgrade pip
RUN pip install transformers

COPY . /app

WORKDIR /app

CMD ["python", "main.py"]