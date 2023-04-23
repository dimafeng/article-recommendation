from intel/intel-optimized-pytorch:1.12.100

COPY . /app

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install autogluon

CMD ["python", "main.py"]